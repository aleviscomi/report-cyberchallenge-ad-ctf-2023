<template>
  <div class="" id="main">
    <b-navbar wrapper-class="container" type="is-light" :shadow="true">
      <template slot="brand">
        <b-navbar-item>
          <!-- <img src="@/assets/mooz.png"/> -->
          <b>MO</b>
          MOOZ
          <b>OZ</b>
        </b-navbar-item>
      </template>
      <!-- <template slot="start">
            <b-navbar-item href="#main">Home</b-navbar-item>
      </template> -->
      <template slot="end">
        <b-navbar-item tag="div">
          <div class="buttons">
      
            <b-button icon-left="sync" size="is-small" class="is-loading" v-if="isLoading && loggedin">Refresh</b-button>
            <b-button icon-left="sync" size="is-small" v-else-if="loggedin" @click="get_users">Refresh</b-button>
      
            <b-button icon-left="user" size="is-small" @click="modaltrigger.isLoginModalActive = true" v-if="!loggedin">Login</b-button>
            <b-button icon-left="sign-out-alt" size="is-small" @click="logout" v-if="loggedin">Logout</b-button>
            <b-button icon-left="user-plus" size="is-small" type="is-info" @click="modaltrigger.isRegisterModalActive = true" v-if="!loggedin">Register</b-button>
            <!-- <b-button icon-left="question-circle" size="is-small" @click="helpdialog">Help</b-button> -->
            <b-button icon-left="question-circle" size="is-small" @click="modaltrigger.isFaqHelpModalActive = true">Help</b-button>
          </div>
        </b-navbar-item>
      </template>
    </b-navbar>
    <div class="container" v-if="!loggedin">
      <front-page :avatar="get_avatar_url('Cat.png')"></front-page>   <!-- import front page -->
      <b-modal 
            v-model="modaltrigger.isLoginModalActive"
            has-modal-card
            trap-focus
            :destroy-on-hide="false"
            aria-role="dialog"
            aria-modal>
      <form action="">
          <div class="modal-card" style="width: auto">
              <header class="modal-card-head">
                  <p class="modal-card-title">Login</p>
                  <button
                      type="button"
                      class="delete"
                      @click="modaltrigger.isLoginModalActive=false"/>
              </header>
              <section class="modal-card-body">
                  <b-field label="Email">
                      <b-input
                          type="email"
                          v-model="userinfo.email"
                          placeholder="Your email"
                          required>
                      </b-input>
                  </b-field>

                  <b-field label="Password">
                      <b-input
                          type="password"
                          v-model="userinfo.password"
                          password-reveal
                          placeholder="Your password"
                          required>
                      </b-input>
                  </b-field>

                  <b-checkbox>Remember me</b-checkbox>
              </section>
              <footer class="modal-card-foot">
                  <button class="button" type="button" @click="modaltrigger.isLoginModalActive = false">Close</button>
                  <button class="button is-primary" @click.prevent="login">Login</button>
              </footer>
          </div>
      </form>
      </b-modal>
      <b-modal 
            v-model="modaltrigger.isRegisterModalActive"
            has-modal-card
            trap-focus
            :destroy-on-hide="false"
            aria-role="dialog"
            aria-modal>
      <form action="">
          <div class="modal-card" style="width: auto">
              <header class="modal-card-head">
                  <p class="modal-card-title">Register</p>
                  <button
                      type="button"
                      class="delete"
                      @click="modaltrigger.isRegisterModalActive=false"/>
              </header>
              <section class="modal-card-body">
                  <b-field label="Username">
                      <b-input
                          type="username"
                          v-model="userinfo.username"
                          placeholder="Your username"
                          required>
                      </b-input>
                  </b-field>
                  <b-field label="Email">
                      <b-input
                          type="email"
                          v-model="userinfo.email"
                          placeholder="Your email"
                          required>
                      </b-input>
                  </b-field>

                  <b-field label="Password">
                      <b-input
                          type="password"
                          v-model="userinfo.password"
                          password-reveal
                          placeholder="Your password"
                          required>
                      </b-input>
                  </b-field>
              </section>
              <footer class="modal-card-foot">
                  <button class="button" type="button" @click="modaltrigger.isRegisterModalActive = false">Close</button>
                  <button class="button is-primary" @click.prevent="addUser(userinfo)">Register</button>
              </footer>
          </div>
      </form>
      </b-modal>
    </div>
    <div class="container" v-else>
      <!-- here the logged in part -->
      <!-- Show on chat view only last 800 users for performance reasons -->
      <chat-view 
        :userinfo="userinfo" 
        :userlist="userlist.slice(-800)"
        :get_avatar_url="get_avatar_url"
        :print_error="print_error"
        :print_json_fail="print_json_fail"
        :print_success="print_success"></chat-view>
    </div>
    <faq-help-view :isComponentModalActive="this.modaltrigger.isFaqHelpModalActive" @closehelp="modaltrigger.isFaqHelpModalActive = false"></faq-help-view>
  </div>
</template>

<script>
import FrontPage from './components/FrontPage.vue'
import ChatView from './components/ChatView.vue'
import FaqHelpView from './components/FaqHelpView.vue'
/* global BigInt */

var baseurl = ''

export default {
  name: "moozfrontend",
  components: {
      FrontPage,
      ChatView,
      FaqHelpView
    },
  data(){
    return {
      loggedin: false,
      userinfo:{
        username:'',
        email:'',
        password:'',
        id: -1,
        avatar: '',
        key: -1
      },
      isLoading : false,
      modaltrigger:{
        isLoginModalActive : false ,
        isRegisterModalActive : false,
        isFaqHelpModalActive : false
      },
      userlist : [],
      timer: null
    }
  },
  methods: {
    print_error(e){ // various errors
        this.$buefy.notification.open({
            message: `Error: ${e}`,
            type: 'is-danger',
            hasIcon: true,})
        // this.loggedin=false
    },
    print_json_fail(res){
        this.$buefy.notification.open({
          message: `Error: ${res.message}`,
          type: 'is-danger',
          hasIcon: true,
        })
    },
    print_success(message){
        this.$buefy.notification.open({
              message: message,
              type: 'is-success',
              hasIcon: true,
          })
    },
    get_avatar_url(avatar){
      return baseurl+'/utils/avatar?filename='+avatar;
    },
    get_users(){
      this.isLoading=true
      fetch(baseurl+'/auth/users', {
                headers: {
                  'Accept': 'application/json',
                  'Content-Type': 'application/json'
                },
                method: 'GET',
                credentials: 'include',
              }).then((body) => body.json())
              .then(res => {
                if (res.status == "fail") {
                  // this.print_json_fail(res)
                  this.loggedin = false
                } else {
                  this.userlist = res.users
                }
              }).catch(this.print_error)
      this.isLoading=false
    },
    chek_login(){
      fetch(baseurl+'/auth/check_login', {
                headers: {
                  'Accept': 'application/json',
                  'Content-Type': 'application/json'
                },
                method: 'GET',
                credentials: 'include',
              }).then((body) => body.json())
              .then(res => {
                if (res.status == "fail") {
                  // this.print_json_fail(res)
                  this.loggedin = false
                } else {
                  this.print_success(`User ${res.user.username} Logged-in. ${res.message}`)
                  this.loggedin=true
                  this.userinfo.username = res.user.username
                  this.userinfo.email = res.user.email
                  this.userinfo.id = res.user.id
                  this.userinfo.key = BigInt(res.user.key)
                  this.userinfo.avatar = res.user.avatar
                  this.modaltrigger.isLoginModalActive = false
                  this.modaltrigger.isRegisterModalActive = false
                  this.get_users()
                }
              }).catch(this.print_error)
    },
    addUser(){
      fetch(baseurl+'/auth/register', {
                headers: {
                  'Accept': 'application/json',
                  'Content-Type': 'application/json'
                },
                method: 'POST',
                credentials: 'include',
                body:JSON.stringify({ email: this.userinfo.email, username: this.userinfo.username, password: this.userinfo.password })
              }).then((body) => body.json())
              .then(res => {
                if (res.status == "fail") {
                  this.print_json_fail(res)
                } else {
                  this.print_success(`User ${this.userinfo.username} created. Please Login`)
                  this.modaltrigger.isLoginModalActive = false
                  this.modaltrigger.isRegisterModalActive = false
                }
              }).catch(this.print_error)
    },
    login(){
      fetch(baseurl+'/auth/login', {
                headers: {
                  'Accept': 'application/json',
                  'Content-Type': 'application/json'
                },
                method: 'POST',
                credentials: 'include',
                body:JSON.stringify({ email: this.userinfo.email, password: this.userinfo.password })
              }).then((body) => body.json())
              .then(res => {
                if (res.status == "fail") {
                  this.print_json_fail(res)
                } else {
                  this.print_success(`User ${res.user.username} Logged-in. ${res.message}`)
                  this.loggedin=true
                  this.userinfo.username = res.user.username
                  this.userinfo.email = res.user.email
                  this.userinfo.id = res.user.id
                  this.userinfo.key = BigInt(res.user.key)
                  this.userinfo.avatar = res.user.avatar
                  this.modaltrigger.isLoginModalActive = false
                  this.modaltrigger.isRegisterModalActive = false
                  this.get_users()
                }
              }).catch(this.print_error)
    },
    helpdialog() {
                this.$buefy.dialog.alert({
                    title: 'Help',
                    message: 'If you need help you can look at the documentation and F.A.Q. page. \
                    <br>If that\'s not enough you can take advantage of the free 24/7 telephone support.',
                    confirmText: 'Ok'
                })
    },
    logout(){
      fetch(baseurl+'/auth/logout', {
                headers: {
                  'Accept': 'application/json',
                  'Content-Type': 'application/json'
                },
                method: 'GET',
                credentials: 'include',
              }).then((body) => body.json())
              .then(res => {
                if (res.status == "fail") {
                  this.print_json_fail(res)
                } else {
                  this.print_success(`Logged out successfully`)
                  this.loggedin = false
                }
              }).catch(this.print_error)
    },
  },
  created() {
      this.chek_login()
      this.get_users()
      this.timer = setInterval(this.get_users, 20000)
    },
    destroyed() {
      clearInterval(this.timer)
    },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
