import { generateKeyPairSync } from 'crypto'

const keypair = generateKeyPairSync('rsa', { modulusLength: 4096 })

export const privateKey = keypair.privateKey.export({ type: 'pkcs1', format: 'pem' }).toString()
export const publicKey = keypair.publicKey.export({ type: 'pkcs1', format: 'pem' }).toString()
