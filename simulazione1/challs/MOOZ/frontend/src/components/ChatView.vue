<!-- 
template edited from https://github.com/BulmaTemplates/bulma-templates/blob/master/templates/inbox.html 
                     https://bulmatemplates.github.io/bulma-templates/templates/inbox.html
-->
<template>
<section>
    <div class="columns" id="mail-app">
        <aside class="column is-3 aside hero is-fullheight">
            <div>
                <div class="mt-4">
                    <div class="box">
                        <article class="media">
                            <div class="media-left">
                            <figure class="image is-64x64">
                                <img :src="get_avatar_url(userinfo.avatar)" class="is-rounded" alt="Image">
                            </figure>
                            </div>
                            <div class="media-content">
                            <div class="content wrapall">
                                <p>
                                <strong>{{userinfo.username}}</strong> <br>
                                <small class="has-text-grey">{{userinfo.email}}</small>
                                </p>
                            </div>
                            </div>
                        </article>
                        </div>
                </div>
                <div class="main">
                    <a href="#" class="item active"><span class="icon"><i class="fa fa-users"></i></span><span class="name">Messages</span></a>
                    <!-- <a href="#" class="item" @click="tododialog"><span class="icon"><i class="fa fa-video"></i></span><span class="name">Video Rooms</span></a> -->
                    <a href="#" class="item" @click="isVideoModalActive = true"><span class="icon"><i class="fa fa-video"></i></span><span class="name">Video Rooms</span></a>
                    <a href="#" class="item" @click="tododialog"><span class="icon"><i class="fa fa-save"></i></span><span class="name">File transfers</span></a>
                </div>
            </div>
        </aside>
        <div class="column is-4 messages hero is-fullheight scrollingcolumn" id="message-feed">

          <div v-for="(user, index) in userlist" class="card" :class="{active: (list_active == index)}" :id="'msg-card-'+index" @click="showMessages(user)" :data-preview-id="index" :key=user.id>
              <div class="" :id="'msg-card-inner-'+index" @click="list_active=index">
                  <div class="card-content">
                      <div class="msg-header">
                          <span class="msg-from">
                              <div class="columns">
                              <div class="column is-3">
                              <figure class="image is-64x64">
                                  <img :src="get_avatar_url(user.avatar)" class="is-rounded" alt="Image">
                              </figure>
                              </div>
                              <div class="column mt-1 is-3 ml-4">
                                  <p><strong>{{user.username}}</strong></p>
                                  <p class="has-text-grey"> <small>{{user.email}}</small></p>
                              </div>
                              </div>
                          </span>
                      </div>
                  </div>
              </div>
          </div>
        </div>
        <div class="column is-5 message hero is-fullheight scrollingcolumn" id="message-pane">
            <div class="box message-preview" v-for="(message, index) in shown_messages" :key=message.id :id="'mess'+index">
                <div class="top"  :class="{invertmirror: (message.userid == userinfo.id) }">
                    <div class="avatar">
                        <img :src="get_avatar_url(userlist.find((a)=>{return a.id==message.userid;}).avatar)">
                    </div>
                    <div class="address"  :class="{invertmirror: (message.userid == userinfo.id) }">
                        <div class="name">{{ userlist.find((a)=>{return a.id==message.userid;}).username }}</div>
                        <div class="has-text-grey"><small>{{ userlist.find((a)=>{return a.id==message.userid;}).email }}</small></div>
                    </div>
                    <hr>
                    <div class="content"  :class="{invertmirror: (message.userid == userinfo.id) }">
                      <small class="is-size-7 has-text-weight-light has-text-grey">{{message.tstamp}}</small>
                        <p>{{message.body}}</p>
                    </div>
                </div>
            </div>

            <div class="box message-preview mb-5" id="mess_send" v-if="list_active != -1">
                <div class="top">
                    <b-field>
                        <b-input placeholder="Message..." expanded type="message" v-model="composebody"></b-input>
                        <p class="control">
                            <b-button class="button is-info" @click="sendMessage(selecteduser)">Send</b-button>
                        </p>
                    </b-field>
                </div>
            </div>
        </div>
    </div>
    <video-view :isComponentModalActive="this.isVideoModalActive" :tododialog="this.tododialog" @closevideo="isVideoModalActive = false"></video-view>
</section>
</template>

<script>
import CryptoJS from 'crypto-js'
/* global BigInt */

var baseurl = ''
var longToByteArray = function(/*long*/long) {
    // we want to represent the input as a 8-bytes array
    var byteArray = [0, 0, 0, 0, 0, 0, 0, 0];
    for ( var index = 0; index < byteArray.length; index ++ ) {
        var byte = long & 0xffn;
        byteArray [ index ] = Number(byte);
        long = (long - byte) / 256n ;
    }
    return byteArray;
};
var universalBtoa = str => {
  try {
    return btoa(str);
  } catch (err) {
    return Buffer.from(str).toString('base64');
  }
};

// bigint because user private is bigger than 53 bits
function powermod(base, exponent, modulus) {
    if (base < 1n || exponent < 0n || modulus < 1n)
        return -1n

    var result = 1n;
    while (exponent > 0n) {
       if ((exponent % 2n) == 1n) {
            result = (result * base) % modulus;
        }
       base = (base * base) % modulus;
      exponent = exponent >> 1n
    }
    return result;
}

import VideoView from './VideoView.vue'
        
export default {
  name: 'ChatView',
  components:{VideoView},
  props: {
    userlist: Array,
    userinfo: Object,
    get_avatar_url: Function,
    print_error: Function,
    print_json_fail: Function,
    print_success: Function,
  },
  data() {
      return {
          shown_messages:[
          ],
          list_active: -1,
          selecteduser: null,
          composebody:'',
          isVideoModalActive: false
      }
  },
  methods:{
      async showMessages(user){
        this.shown_messages=[]
        var publickey
        var params
        try{
          let publicreq = await fetch (baseurl + '/crypto/get_public/'+user.id,{
            headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                  },
                  method: 'GET',
                  credentials: 'include',
          })
          let publicjson = await publicreq.json()
          if(publicjson.status == "ok")
            publickey = BigInt(publicjson.public)
          else
            this.print_json_fail(publicjson)
        }catch (err) {this.print_error(err)}
        try{
          let paramsreq = await fetch (baseurl + '/crypto/get_params',{
            headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                  },
                  method: 'GET',
                  credentials: 'include',
          })
          let paramsjson = await paramsreq.json()
          if(paramsjson.status=="ok"){
            params = { g : BigInt(paramsjson.params.g), p: BigInt(paramsjson.params.p) }
          }
          else
            this.print_json_fail(paramsjson)
        }catch (err) {this.print_error(err)}

        console.log(params)
        console.log(publickey)

        fetch(baseurl+'/messages/'+this.userinfo.id+'/'+user.id, {
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
                  var computedkey = powermod(BigInt(publickey),this.userinfo.key, BigInt(params.p))
                  // console.log(this.userinfo.key)
                  // console.log(computedkey)

                  var arraybuf = longToByteArray(computedkey & 0xffffffffffffffn) // DES key is 56 bits
                  var myb64key = universalBtoa(String.fromCharCode(...new Uint8Array(arraybuf)));
                  try {
                  var decrypted = CryptoJS.DES.decrypt(
                          {ciphertext: CryptoJS.enc.Base64.parse(res.data)}, 
                          CryptoJS.enc.Base64.parse(myb64key) , 
                          {mode: CryptoJS.mode.ECB, padding: CryptoJS.pad.NoPadding}
                          ).toString(CryptoJS.enc.Utf8).trim()
                  this.shown_messages = JSON.parse(decrypted)
                  } catch (err){
                    this.print_error(err)
                  }
                }
              }).catch(this.print_error)
        this.selecteduser=user
      },
      sendMessage(user){
        if(this.composebody==''){
          this.$buefy.notification.open({
            message: `Message is empty`,
            type: 'is-warning',
            hasIcon: true,})
        }else{
          fetch(baseurl+'/send' , {
                  headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                  },
                  method: 'POST',
                  credentials: 'include',
                  body:JSON.stringify({ receiver:user.id, body:this.composebody })
                }).then((body) => body.json())
                .then(res => {
                  if (res.status == "fail") {
                    this.print_json_fail(res)
                  } else {
                    this.print_success(`Successfully Sent Message to ${user.username}`)
                    this.showMessages(user)
                  }
                }).catch(this.print_error)
          this.composebody=''
        }
      },
      tododialog() {
                this.$buefy.dialog.alert({
                    title: 'TODO',
                    message: 'This functionality is still under active development. <br> Please wait for the next update\
                    to enjoy this awsome communication functionality.',
                    confirmText: 'Ok'
                })
    },
  }
  
}
</script>

<style>
html{
  overflow-y: hidden !important;
}
</style>

<style scoped>
html,body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
  font-size: 14px;
  line-height: 1.5;
  height: 100%;
  background-color: #fff;
}
.nav.is-dark {
  background-color: #232B2D;
  color: #F6F7F7;
}
.nav.is-dark .nav-item a, .nav.is-dark a.nav-item {
    color: #F6F7F7;
}
.nav.is-dark .nav-item a.button.is-default {
    color: #F6F7F7;
    background-color: transparent;
    border-width: 2px;
}
.nav.menu {
  border-bottom: 1px solid #e1e1e1;
}
.nav.menu .nav-item .icon-btn {
  border: 3px solid #B7C6C9;
  border-radius: 90px;
  padding: 5px 7px;
  color: #B7C6C9;
}
.nav.menu .nav-item.is-active .icon-btn {
  color: #2EB398;
  border: 3px solid #2EB398;
}
.nav.menu .nav-item .icon-btn .fa {
  font-size: 20px;
  color: #B7C6C9;
}
.nav.menu .nav-item.is-active .icon-btn .fa {
  color: #2EB398;
}
.aside {
  display:block;
  /* background-color: #F9F9F9; */
  background-color: #ffffff;
  border-right: 1px solid #DEDEDE;
}
.messages {
  display:block;
  background-color: #fff;
  border-right: 1px solid #DEDEDE;
  padding: 30px 20px;
}
.message {
  display:block;
  background-color: #fff;
  padding: 30px 20px;
}
.aside .compose {
  height: 95px;
  margin:0 -10px;
  padding: 25px 30px;
}
.aside .compose .button {
  color: #F6F7F7;
}
.aside .compose .button .compose {
  font-size: 14px;
  font-weight: 700;
}
.aside .main {
  padding: 40px;
  color: #6F7B7E;
  color: #ffffff

}
.aside .title {
  color: #6F7B7E;
  font-size: 12px;
  font-weight: bold;
  text-transform: uppercase;
}
.aside .main .item {
  display: block;
  padding: 10px 0;
  color: #6F7B7E;
}
.aside .main .item.active {
  background-color: #F1F1F1;
  margin: 0 -50px;
  padding-left: 50px;
}
.aside .main .item:active,.aside .main .item:hover {
  background-color: #F2F2F2;
  margin: 0 -50px;
  padding-left: 50px;
}
.aside .main .icon {
  font-size: 19px;
  padding-right: 30px;
  color: #A0A0A0;
}
.aside .main .name {
  font-size: 15px;
  color: #5D5D5D;
  font-weight: 500;
}
.messages .action-buttons {
  padding: 0;
  margin-top: -20px;
}
.message .action-buttons {
  padding: 0;
  margin-top: -5px;
}
.action-buttons .control.is-grouped {
  display: inline-block;
  margin-right: 30px;
}
.action-buttons .control.is-grouped:last-child {
  margin-right: 0;
}
.action-buttons .control.is-grouped .button:first-child {
  border-radius: 5px 0 0 5px;
}
.action-buttons .control.is-grouped .button:last-child {
  border-radius: 0 5px 5px 0;
}
.action-buttons .control.is-grouped .button {
  margin-right: -5px;
  border-radius: 0;
}
.pg {
  display: inline-block;
  top:10px;
}
.is-grouped .button {
  background-image: linear-gradient(#F8F8F8, #F1F1F1);
}
.is-grouped .button .fa {
  font-size: 15px;
  color: #AAAAAA;
}
/* .inbox-messages {
  margin-top:60px;
} */
/* .message-preview {
  margin-top: 60px;
} */
.inbox-messages .card {
  width: 100%;
}
.inbox-messages strong {
  color: #5D5D5D;
}
.inbox-messages .msg-check {
  padding: 0 20px;
}
.inbox-messages .msg-subject {
  padding: 10px 0;
  color: #5D5D5D;
}
.inbox-messages .msg-attachment {
  float:right;
}
.inbox-messages .msg-snippet {
  padding: 5px 20px 0px 5px;
}
.inbox-messages .msg-subject .fa {
  font-size: 14px;
  padding:3px 0;
}
.inbox-messages .msg-timestamp {
  float: right;
  padding: 0 20px;
  color: #5D5D5D;
}
.message-preview .avatar {
  display: inline-block;
}
.message-preview .top .address {
  display: inline-block;
  padding: 0 20px;
}
.avatar img {
  width: 40px;
  border-radius: 50px;
  border: 2px solid #999;
  padding: 2px;
}
.address .name {
  font-size: 16px;
  font-weight: bold;
}
.address .email {
  font-weight: bold;
  color: #B6C7D1;
}
.card.active {
  background-color:#F5F5F5;
}
.invertmirror {
    transform: scale(-1,1);
}
.scrollingcolumn{
  height: 1px; 
  overflow-y: scroll
}
.hero.is-fullheight {
    min-height: calc(100vh - 3.25rem);
}
.card:last-of-type{
    margin-bottom: 1.5rem !important;
}
.wrapall {
  word-break: break-all;
  word-wrap: break-word;
}
</style>