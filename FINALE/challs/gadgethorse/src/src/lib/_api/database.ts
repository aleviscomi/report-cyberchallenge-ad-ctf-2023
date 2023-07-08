import { Kysely, MysqlDialect } from 'kysely'
import type { DB } from './db'
import { createPool } from 'mysql2'
import dotenv from 'dotenv'

dotenv.config()

declare global {
	// eslint-disable-next-line @typescript-eslint/no-namespace
	namespace NodeJS {
		interface ProcessEnv {
			DATABASE_USER: string
			DATABASE_PASSWORD: string
			DATABASE_HOST: string
			DATABASE_DB: string
		}
	}
}

const db = new Kysely<DB>({
	dialect: new MysqlDialect({
		pool: createPool({
			user: process.env.DATABASE_USER,
			password: process.env.DATABASE_PASSWORD,
			host: process.env.DATABASE_HOST,
			database: process.env.DATABASE_DB
		})
	})
})

export default db
