<template>
    <section>
        <b-modal 
            v-model="isComponentModalActive"
            has-modal-card
            full-screen 
            :can-cancel="false">
            <div class="modal-card" style="width: auto">
                <header class="modal-card-head">
                    <p class="modal-card-title">Help and F.A.Q.</p>
                </header>
                <section class="modal-card-body">
                    <div class="container">
                        <h2 class="has-text-weight-bold is-size-4 mb-4 ml-2">Help</h2>
                        <p class="ml-2">MOOZ is a new messaging platform that allows for free and secure communications.
                            <br>
                            Among its features there are <strong> E2E encrypted chats </strong>, <strong>file transfers</strong> and <strong>video conferencing</strong>.
                            <br>
                            All ours developers are working as hard as they can to provide you with the best features with <strong>uncompromised security</strong>.
                        </p>
                        <p class="ml-2 mt-2">For questions you can take a loook at the section below, <br> if that's not enough you can take advantage of the free 24/7 telephone support.</p>
                        <hr>
                        <div class="mt-5">
                            <h2 class="has-text-weight-bold is-size-5 mb-4 ml-2">F.A.Q.</h2>
                            
                            <b-collapse
                                class="card"
                                animation="slide"
                                v-for="(collapse, index) of collapses"
                                :key="index"
                                :open="isOpen == index"
                                @open="isOpen = index">
                                <div
                                    slot="trigger"
                                    slot-scope="props"
                                    class="card-header"
                                    role="button">
                                    <p class="card-header-title">
                                        {{ collapse.title }}
                                    </p>
                                    <a class="card-header-icon">
                                        <b-icon
                                            :icon="props.open ? 'menu-down' : 'menu-up'">
                                        </b-icon>
                                    </a>
                                </div>
                                <div class="card-content">
                                    <div class="content">
                                        {{ collapse.text }}
                                    </div>
                                </div>
                            </b-collapse>
                        </div>
                    </div>
                </section>
                <footer class="modal-card-foot">
                    <button class="button" type="button" @click="$emit('closehelp')">Close</button>
                    <!-- <button class="button is-primary" >Ok</button> -->
                </footer>
            </div>
        </b-modal>
    </section>
</template>

<script>
    export default {
        name:"VideoView",
        props : ['isComponentModalActive'],
        data() {
            return {
                isOpen:-1,
                collapses:[
                    {
                        title: 'Can i change my avatar?',
                        text: 'For now the avatar is assigned randomly from our vast collection and is not modifiable'
                    },
                    {
                        title: 'Can i change my profile info?',
                        text: 'For now the profile is immutable.. you can always create another one!'
                    },
                    {
                        title: 'Can i delete my profile info?',
                        text: 'For now the profile is immutable.. if you want to delete your profile contact the telephone support'
                    },
                    {
                        title: 'How my messages are encrypted?',
                        text: 'Chats are encrypted with state-of-the-art encryption, using a the most robust handshake\
                        mechanism in existance to create a new session key for every sender, receiver tuple.'
                    },
                    {
                        title: 'How about the missing features?',
                        text: 'Our developer are at work night and day to provide all the functionality as soon as possible\
                        please be patient, it won\'t take long!'
                    },
                    {
                        title: 'How data is stored?',
                        text: 'Data is stored in our databse cluster protected by strong authentication and encryption'
                    }

                ],
                videoactive:false,
            }
        },
    }
</script>

<style scoped>

</style>