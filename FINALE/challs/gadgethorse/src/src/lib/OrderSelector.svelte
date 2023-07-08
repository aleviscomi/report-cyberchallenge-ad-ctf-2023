<script lang="ts">
	type T = $$Generic

	export let options: T[]
	export let value: T

	let id = 'id_' + Math.random().toString(36).substring(2)
</script>

<div class="grid w-full" style="grid-template-columns: repeat({options.length}, minmax(0, 1fr))">
	{#each options as option, idx}
		<div class="w-full">
			<input
				type="radio"
				value="{option}"
				name="{id}"
				class="peer hidden"
				bind:group="{value}"
				on:change
				id="{id}_{idx}" />
			<label
				for="{id}_{idx}"
				class="hover:bg-off block w-full cursor-pointer text-center text-2xl peer-checked:bg-salmon peer-checked:bg-opacity-50 peer-checked:hover:bg-opacity-80 {idx ===
				0
					? 'rounded-l-md border-r-transparent'
					: idx === options.length - 1
					? 'rounded-r-md'
					: 'border-r-transparent'} border border-neutral-400 py-3">
				<slot value="{option}" />
			</label>
		</div>
	{/each}
</div>
