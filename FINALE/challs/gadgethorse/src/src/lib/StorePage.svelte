<script lang="ts">
	import LoadingForm from '$lib/LoadingForm.svelte'
	import PriceViewer from '$lib/PriceViewer.svelte'

	let quantity = 1

	export let data: { name: string; description: string[]; price: number }

	function change(delta: number) {
		quantity += delta
		validate()
	}

	function validate() {
		if (quantity < 1) {
			quantity = 1
		} else if (quantity > 1000) {
			quantity = 1000
		}
	}
</script>

<div class="items-center justify-center py-14 md:flex md:h-full">
	<div class="container grid grid-cols-1 gap-24 lg:grid-cols-2">
		<div class="">
			<slot name="image" />
		</div>
		<div class="mx-auto w-full md:w-9/12 lg:w-full">
			<h1 class="mb-4 text-4xl font-bold">{data.name}</h1>
			{#each data.description as paragraph}
				<p class="mb-5">
					{paragraph}
				</p>
			{/each}

			<LoadingForm class="mt-8">
				<slot />
				<div class="mt-4 font-semibold">Quantity:</div>
				<div class="mt-2 flex justify-between">
					<div class="flex">
						<button
							type="button"
							on:click="{() => change(-1)}"
							class="hover:bg-off flex h-full items-center justify-center rounded-l-md border border-r-0 border-neutral-400 px-5 text-2xl font-bold"
							>-</button>
						<input
							class="z-10 m-0 h-full w-20 border border-neutral-400 focus:border-primary focus:ring-primary"
							type="number"
							min="1"
							max="1000"
							id="qty"
							name="qty"
							on:change="{validate}"
							bind:value="{quantity}" />
						<button
							type="button"
							on:click="{() => change(1)}"
							class="hover:bg-off flex h-full items-center justify-center rounded-r-md border border-l-0 border-neutral-400 px-5 text-2xl font-bold"
							>+</button>
					</div>
					<div class="self-center text-xl font-semibold">
						<PriceViewer value="{data.price * Math.min(quantity, 1000)}" />
					</div>
					<div>
						<button
							class="rounded-md bg-salmon px-10 py-3 font-semibold text-white hover:bg-[#F56B56]"
							>Add to cart</button>
					</div>
				</div>
			</LoadingForm>
		</div>
	</div>
</div>
