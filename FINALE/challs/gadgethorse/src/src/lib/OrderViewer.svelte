<script lang="ts">
	import { enhance } from '$app/forms'
	import PriceViewer from '$lib/PriceViewer.svelte'
	import type { CartItem } from '$lib/_api/utils'

	export let orderId = ''
	export let items: CartItem[]

	export let orderInfo:
		| {
				name: string
				surname: string
				address: string
				city: string
				country: string
		  }
		| undefined = undefined

	export let isCart = false

	$: price = items.reduce((acc, el) => acc + el.qty * el.price, 0)

	$: taxes = Math.floor((price / 1.22) * 0.22)
	$: noTaxes = price - taxes
	$: shipping = items.length > 0 ? 1337 : 0
	$: total = noTaxes + taxes + shipping
</script>

<div class="container py-16">
	<h1 class="text-4xl font-bold">
		{#if isCart}
			Cart
		{:else}
			Order #{orderId}
		{/if}
	</h1>

	<div class="mt-8 grid grid-cols-[2fr,1fr] gap-4">
		<div>
			{#if items.length === 0}
				<div class="py-12 text-center italic">Your cart is empty</div>
			{:else}
				<table class="w-full border-separate border-spacing-2">
					<thead>
						<th>Description</th>
						<th>Quantity</th>
						<th>Total</th>
						{#if isCart}
							<th></th>
						{/if}
					</thead>
					<tbody>
						{#each items as item, idx}
							<tr>
								<td class="flex items-center gap-8">
									<img src="{item.image}" class="aspect-[226/192] h-auto w-24" alt="" />
									<div>
										<div class="hidden" data-name="id">{item.id}</div>
										<a class="font-semibold text-dark-green hover:underline" href="{item.href}"
											>{item.name}</a>
										<div class="text-sm">{item.description}</div>
									</div>
								</td>
								<td class="text-center">{item.qty}</td>
								<td class="text-center"><PriceViewer value="{item.price * item.qty}" /></td>
								{#if isCart}
									<td>
										<form action="/cart/?/delete" method="POST" use:enhance>
											<input type="hidden" name="product" id="product" value="{item.id}" />
											<button class="rounded-full p-2 text-primary">
												<svg
													xmlns="http://www.w3.org/2000/svg"
													viewBox="0 0 24 24"
													fill="currentColor"
													class="h-6 w-6">
													<path
														fill-rule="evenodd"
														d="M16.5 4.478v.227a48.816 48.816 0 013.878.512.75.75 0 11-.256 1.478l-.209-.035-1.005 13.07a3 3 0 01-2.991 2.77H8.084a3 3 0 01-2.991-2.77L4.087 6.66l-.209.035a.75.75 0 01-.256-1.478A48.567 48.567 0 017.5 4.705v-.227c0-1.564 1.213-2.9 2.816-2.951a52.662 52.662 0 013.369 0c1.603.051 2.815 1.387 2.815 2.951zm-6.136-1.452a51.196 51.196 0 013.273 0C14.39 3.05 15 3.684 15 4.478v.113a49.488 49.488 0 00-6 0v-.113c0-.794.609-1.428 1.364-1.452zm-.355 5.945a.75.75 0 10-1.5.058l.347 9a.75.75 0 101.499-.058l-.346-9zm5.48.058a.75.75 0 10-1.498-.058l-.347 9a.75.75 0 001.5.058l.345-9z"
														clip-rule="evenodd"></path>
												</svg>
											</button>
										</form>
									</td>
								{/if}
							</tr>
							{#if idx !== items.length - 1}
								<tr>
									<td colspan="{isCart ? 4 : 3}">
										<hr class="my-2" />
									</td>
								</tr>
							{/if}
						{/each}
					</tbody>
				</table>
			{/if}
		</div>
		<div>
			<div class="bg-off rounded-lg px-10 py-8">
				<h2 class="text-2xl font-bold">Price</h2>
				<table class="w-full">
					<tr>
						<td class="py-1.5 pt-5">Gadgets</td>
						<td class="py-1.5 pt-5 text-right"><PriceViewer value="{noTaxes}" /></td>
					</tr>
					<tr>
						<td>Taxes</td>
						<td class="py-1.5 text-right"><PriceViewer value="{taxes}" /></td>
					</tr>
					<tr>
						<td>Shipping</td>
						<td class="py-1.5 text-right"><PriceViewer value="{shipping}" /></td>
					</tr>
					<tr>
						<td colspan="2">
							<hr class="my-4 border-neutral-500" />
						</td>
					</tr>
					<tr class="w-full text-lg">
						<td class="font-semibold">Total</td>
						<td class="py-1.5 text-right font-semibold"><PriceViewer value="{total}" /></td>
					</tr>
				</table>
			</div>
			{#if orderInfo}
				<div class="bg-off mt-6 rounded-lg px-10 py-8">
					<h2 class="text-2xl font-bold">Shipment details</h2>
					<table class="w-full">
						<tr>
							<td class="py-1.5 pt-5">Name</td>
							<td class="py-1.5 pt-5 text-right">{orderInfo.name}</td>
						</tr>
						<tr>
							<td>Surname</td>
							<td class="py-1.5 text-right">{orderInfo.surname}</td>
						</tr>
						<tr>
							<td>Address</td>
							<td class="py-1.5 text-right">{orderInfo.address}</td>
						</tr>
						<tr>
							<td>City</td>
							<td class="py-1.5 text-right">{orderInfo.city}</td>
						</tr>
						<tr>
							<td>Country</td>
							<td class="py-1.5 text-right">{orderInfo.country}</td>
						</tr>
					</table>
				</div>
			{/if}
			{#if !isCart}
				<a
					href="/order/{orderId}/receipt"
					class="mt-6 block w-full rounded-md bg-salmon px-10 py-3 text-center font-semibold text-white hover:bg-[#F56B56]"
					>Download receipt</a>
			{/if}
		</div>
	</div>
</div>
