<template>
    <section>
        <b-modal 
            v-model="isComponentModalActive"
            has-modal-card
            full-screen 
            :can-cancel="false">
            <div class="modal-card" style="width: auto">
                <header class="modal-card-head">
                    <p class="modal-card-title">Join Video</p>
                </header>
                <video autoplay="true" id="videoElement" style="height:50%;" ref="videoelem" @click="startvideo"></video><br>
                <section class="modal-card-body">
                    <p class="has-text-weight-light is-size-7 mb-4 mt-0">Click on video area to start video preview</p>
                    <b-field label="Room Name">
                        <b-input
                            type="text"
                            placeholder="Room name"
                            required>
                        </b-input>
                    </b-field>

                    <b-checkbox>Unmute Audio</b-checkbox>
                </section>
                <footer class="modal-card-foot">
                    <button class="button" type="button" @click="$emit('closevideo')">Close</button>
                    <button class="button is-primary" @click="tododialog">Start Video Room</button>
                </footer>
            </div>
        </b-modal>
    </section>
</template>

<script>
    export default {
        name:"VideoView",
        props : ['isComponentModalActive', 'tododialog'],
        data() {
            return {
                videoactive:false,
            }
        },
        methods:{
            startvideo(videoel){
                this.videoactive = true
                var video = videoel.srcElement

                if (navigator.mediaDevices.getUserMedia) {
                navigator.mediaDevices.getUserMedia({ video: true })
                    .then(function (stream) {
                    video.srcObject = stream;
                    })
                    .catch(function () {
                    console.log("Something went wrong!");
                    });
                }
            }
        }
    }
</script>

<style scoped>

</style>