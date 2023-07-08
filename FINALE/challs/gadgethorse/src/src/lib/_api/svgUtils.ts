import type { Cookies } from '@sveltejs/kit'
import { getCartCookie, getSessionCookie } from './utils'
import db from './database'

export const findUserProduct = async (
	cookies: Cookies,
	id: string,
	type: 'custom-sticker' | 'custom-shirt'
) => {
	const cart = getCartCookie(cookies)
	const user = getSessionCookie(cookies)

	// Search this id in orderd items
	const orderedProduct =
		user &&
		(await db
			.selectFrom('order_items')
			.innerJoin('customizations', 'order_items.item', 'customizations.id')
			.innerJoin('order', 'order_items.order', 'order.id')
			.select([
				'customizations.id',
				'customizations.base_product',
				'customizations.color',
				'customizations.font',
				'customizations.height',
				'customizations.text',
				'customizations.width',
				'customizations.x',
				'customizations.y',
				'order.user'
			])
			.where('base_product', '=', type)
			.where('order_items.item', '=', id)
			.where('order.user', '=', user.id)
			.executeTakeFirst())

	// Look for it in the cart
	if (cart.every((e) => e.id !== id) && !orderedProduct) {
		return null
	}

	const product =
		orderedProduct ||
		(await db
			.selectFrom('customizations')
			.selectAll()
			.where('base_product', '=', type)
			.where('id', '=', id)
			.executeTakeFirst())

	if (!product) {
		return null
	}

	return product
}

export const generateSVGResponse = (
	item: NonNullable<Awaited<ReturnType<typeof findUserProduct>>>,
	customElements = '',
	dropShadow = true
) => {
	const svg = `<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
    viewBox="0 0 ${item.width} ${item.height}"
    dominant-baseline="middle"
    text-anchor="middle"
    paint-order="stroke"
    stroke-linecap="butt"
    stroke-linejoin="round"
    ${dropShadow ? 'style="filter: drop-shadow(0px 0px 3px #777);"' : ''}
    xmlns="http://www.w3.org/2000/svg"
    xmlns:svg="http://www.w3.org/2000/svg"
>
    <style>
        /* latin */
        @font-face {
        font-family: 'Comic Neue';
        font-style: normal;
        font-weight: 700;
        font-display: swap;
        src: url(https://fonts.gstatic.com/s/comicneue/v8/4UaErEJDsxBrF37olUeD_xHM8pxULg.woff2)
        format('woff2');
        unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC,
        U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215,
        U+FEFF, U+FFFD;
        }
        /* latin-ext */
        @font-face {
        font-family: 'Pacifico';
        font-style: normal;
        font-weight: 400;
        font-display: swap;
        src: url(https://fonts.gstatic.com/s/pacifico/v22/FwZY7-Qmy14u9lezJ-6J6MmTpA.woff2)
        format('woff2');
        unicode-range: U+0100-02AF, U+0304, U+0308, U+0329, U+1E00-1E9F, U+1EF2-1EFF, U+2020,
        U+20A0-20AB, U+20AD-20CF, U+2113, U+2C60-2C7F, U+A720-A7FF;
        }
        /* latin */
        @font-face {
        font-family: 'Pacifico';
        font-style: normal;
        font-weight: 400;
        font-display: swap;
        src: url(https://fonts.gstatic.com/s/pacifico/v22/FwZY7-Qmy14u9lezJ-6H6Mk.woff2)
        format('woff2');
        unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC,
        U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215,
        U+FEFF, U+FFFD;
        }
        /* latin-ext */
        @font-face {
        font-family: 'Press Start 2P';
        font-style: normal;
        font-weight: 400;
        font-display: swap;
        src:
        url(https://fonts.gstatic.com/s/pressstart2p/v15/e3t4euO8T-267oIAQAu6jDQyK3nbivN04w.woff2)
        format('woff2');
        unicode-range: U+0100-02AF, U+0304, U+0308, U+0329, U+1E00-1E9F, U+1EF2-1EFF, U+2020,
        U+20A0-20AB, U+20AD-20CF, U+2113, U+2C60-2C7F, U+A720-A7FF;
        }
        /* latin */
        @font-face {
        font-family: 'Press Start 2P';
        font-style: normal;
        font-weight: 400;
        font-display: swap;
        src: url(https://fonts.gstatic.com/s/pressstart2p/v15/e3t4euO8T-267oIAQAu6jDQyK3nVivM.woff2)
        format('woff2');
        unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC,
        U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215,
        U+FEFF, U+FFFD;
        }
    </style>
    ${customElements}
    <text style='stroke: white; stroke-width: 4; font-family: sans-serif; font-weight: bold; fill: #222222; font-family: ${
			item.font
		}'
        x="${item.x}"
        y="${item.y}"
    >${item.text}</text>
</svg>
    `

	return new Response(svg, {
		headers: {
			'Content-Type': 'image/svg+xml',
			'Cache-Control': 's-maxage=604800'
		}
	})
}
