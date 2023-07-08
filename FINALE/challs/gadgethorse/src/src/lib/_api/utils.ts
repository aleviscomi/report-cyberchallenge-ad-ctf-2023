import type { Cookies } from '@sveltejs/kit'
import jwt from 'jsonwebtoken'
import { privateKey, publicKey } from './secrets'
import db from './database'
import libxmljs from 'libxmljs'
import type { XMLElement, XMLText } from 'libxmljs/dist/lib/node'

export type CartItem = {
	id: string
	name: string
	description: string
	href: string
	image: string
	price: number
	qty: number
}

export type CartCookieItem = { id: string; qty: number }

/**
 * Set the session cookie with basic user information
 * @param cookies
 * @param user
 */
export const setSessionCookie = (
	cookies: Cookies,
	user: { id: string; email: string; name: string }
) => {
	cookies.set(
		'session',
		jwt.sign(
			{ id: user.id, email: user.email, name: user.name, exp: Date.now() / 1000 + 60 * 60 },
			privateKey,
			{ algorithm: 'RS256' }
		),
		{
			path: '/',
			secure: false,
			httpOnly: true,
			sameSite: 'strict',
			maxAge: 60 * 60
		}
	)
}

/**
 * Try to retrieve and validate the session cookie
 * @param cookies
 * @returns
 */
export const getSessionCookie = (cookies: Cookies) => {
	try {
		return jwt.verify(cookies.get('session') ?? '', publicKey) as
			| {
					id: string
					name: string
					email: string
			  }
			| null
			| undefined
	} catch {
		return null
	}
}

/**
 * Update the user's cart
 * @param cookies
 * @param cart
 * @param user
 */
export const setCartCookie = async (
	cookies: Cookies,
	cart: unknown[],
	user: { id: string } | null
) => {
	if (user) {
		// Save the cart in the db for next login
		await db
			.updateTable('saved_cart')
			.where('user', '=', user.id)
			.set({
				cart: JSON.stringify(cart)
			})
			.execute()
	}

	cookies.set('cart', Buffer.from(JSON.stringify(cart)).toString('base64url'), {
		path: '/',
		secure: false,
		httpOnly: true,
		sameSite: 'strict',
		maxAge: 60 * 60
	})
}

/**
 * Read the user's cart from the cookies
 * @param cookies
 * @returns
 */
export const getCartCookie = (cookies: Cookies) => {
	const cart = cookies.get('cart') ?? ''

	let cartContent: CartCookieItem[]
	try {
		cartContent = JSON.parse(Buffer.from(cart, 'base64url').toString())
	} catch {
		cartContent = []
	}
	return cartContent
}

/**
 * Retrieve all cart's items information from db
 * @param cart
 * @returns
 */
export const getCartData = async (cart: CartCookieItem[]) => {
	if (cart.length === 0) {
		return []
	}
	const cartData: CartItem[] = []

	const qtyMap: Record<string, number> = {}
	cart.forEach((el) => {
		qtyMap[el.id] = el.qty
	})

	const standardProducts = (
		await db
			.selectFrom('products')
			.selectAll()
			.where(
				'id',
				'in',
				cart.map((el) => el.id)
			)
			.execute()
	).map((el) => ({
		qty: qtyMap[el.id],
		id: el.id,
		name: el.name,
		description: el.short_description,
		price: el.price,
		image: el.image,
		href: `/sticker/${el.id}`
	}))

	const customizedProducts = (
		await db
			.selectFrom('customizations')
			.innerJoin('base_custom_product', 'customizations.base_product', 'base_custom_product.id')
			.select([
				'customizations.id',
				'customizations.text',
				'base_custom_product.name',
				'base_custom_product.price',
				'base_custom_product.image',
				'customizations.base_product'
			])
			.where(
				'customizations.id',
				'in',
				cart.map((el) => el.id)
			)
			.execute()
	).map((el) => ({
		qty: qtyMap[el.id],
		id: el.id,
		name: el.name,
		description: `"${el.text}"`,
		price: el.price,
		image: `/${el.base_product}/${el.id}`,
		href: `/${el.base_product}`
	}))

	Array.prototype.push.apply(cartData, standardProducts)
	Array.prototype.push.apply(cartData, customizedProducts)

	return cartData
}

/**
 * Extract custom data from the sticker/shirt svg
 * @param svg
 * @returns
 */
export const parseCustomSVG = (svg: string) => {
	try {
		const xml = libxmljs.parseXml(svg, { replaceEntities: true })

		const text = (xml.find('//text')[0] as XMLText | undefined)?.text()
		const viewbox = (xml.find('//svg')[0] as XMLElement)
			?.getAttribute('viewBox')
			?.value()
			?.split(' ')
		const width = viewbox && viewbox[2]
		const height = viewbox && viewbox[3]
		const style = (xml.find('//text')[0] as XMLText | undefined)?.getAttribute('style')?.value()
		const font =
			style &&
			style.split('font-family: ')[1] &&
			style.split('font-family: ')[1].split(';')[0].trim()
		const color = (xml.find('//svg')[0] as XMLElement)?.getAttribute('class')?.value()
		const x = (xml.find('//text')[0] as XMLText)?.getAttribute('x')?.value()
		const y = (xml.find('//text')[0] as XMLText)?.getAttribute('y')?.value()

		return {
			text,
			width: parseFloat(width ?? ''),
			height: parseFloat(height ?? ''),
			x: parseFloat(x ?? ''),
			y: parseFloat(y ?? ''),
			font,
			color
		}
	} catch {
		return {
			text: undefined,
			width: undefined,
			height: undefined,
			x: undefined,
			y: undefined,
			font: undefined,
			color: undefined
		}
	}
}
