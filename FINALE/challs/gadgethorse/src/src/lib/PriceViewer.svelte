<script lang="ts">
	export let value: number
</script>

€ {Math.floor(value / 100)},{(value % 100).toString().padStart(2, '0')}
