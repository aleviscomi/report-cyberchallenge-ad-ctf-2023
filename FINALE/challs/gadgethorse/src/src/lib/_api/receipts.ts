import type { CartItem } from './utils'
import fs from 'fs'

const BASE_PATH = `/data/receipts/`

export const createReceiptFile = (
	user: { id: string },
	orderInfo: {
		id: string
		name: string
		surname: string
		address: string
		city: string
		country: string
	},
	cart: CartItem[]
) => {
	const path = `${BASE_PATH}${user.id}/`
	if (!fs.existsSync(path)) {
		fs.mkdirSync(path, { recursive: true })
	}
	fs.writeFileSync(
		`${path}${orderInfo.id}.csv`,
		`Name,${orderInfo.name},,
Surname,${orderInfo.surname},,
Address,${orderInfo.address},,
City,${orderInfo.city},,
Country,${orderInfo.country},,
,,,
,,,
Item,Quantity,Price,
` + cart.map((el) => `${el.name},${el.qty},${el.price},`).join('\n')
	)
}

export const readReceipt = (user: { id: string }, orderId: string) => {
	try {
		return fs.readFileSync(`${BASE_PATH}${user.id}/${orderId}.csv`)
	} catch {
		return null
	}
}
