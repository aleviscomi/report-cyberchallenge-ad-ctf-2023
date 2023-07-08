<script lang="ts">
	import { enhance } from '$app/forms'

	let clazz = ''
	export { clazz as class }
	export let method = 'POST'
	export let action: string | undefined = undefined

	let loading = false
</script>

<form
	class="{clazz}"
	method="{method}"
	action="{action}"
	use:enhance="{() => {
		loading = true
		return async ({ update }) => {
			await update()
			loading = false
		}
	}}">
	<div class="contents" class:invisible="{loading}">
		<slot />
	</div>
	<div class="absolute inset-0 flex items-center justify-center" class:hidden="{!loading}">
		<svg
			class="h-20 w-20 animate-spin text-primary"
			xmlns="http://www.w3.org/2000/svg"
			fill="none"
			viewBox="0 0 24 24">
			<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"
			></circle>
			<path
				class="opacity-75"
				fill="currentColor"
				d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
			></path>
		</svg>
	</div>
</form>
