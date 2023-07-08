<template>
    <section class="hero is-info is-medium">
        <div class="hero-body">
          <div class="container">
            <h1 class="title">
              MOOZ
            </h1>
            <h2 class="subtitle">
              The New and Revolutionary communication platform
            </h2>
            <p>MOOZ offers the next generation communication capabilities with encrypted text chats and P2P video conferences.</p>
            <p>The best part? MOOZ is FREE!</p>
            <div class="columns mt-5 pt-5">
              <div class="column">
                <div class="box">
                  <article class="media">
                    <div class="media-content">
                      <div class="content">
                        <p>
                          <strong>Military grade encryption!</strong>
                          <br>
                          Be assured that you communications are protected by state-of-the-art &trade; E2E encryption
                        </p>
                      </div>
                      
                    </div>
                  </article>
                </div>
              </div>
              <div class="column">
                <div class="box">
                  <article class="media">
                    <div class="media-left">
                      <figure class="image is-64x64">
                        <!-- <img src="https://bulma.io/images/placeholders/128x128.png" alt="Image"> -->
                        <img :src="avatar" alt="Image">
                      </figure>
                    </div>
                    <div class="media-content">
                      <div class="content">
                        <p>
                          <strong>John Smith</strong> <small>@johnsmith</small> <small>31m</small>
                          <br>
                          Mooz changed the way we communicate in this difficult period! It provides all we need to stay in touch assuring the best security features
                        </p>
                      </div>
                      <nav class="level is-mobile">
                        <div class="level-left">
                          <a class="level-item" aria-label="reply">
                            <span class="icon is-small">
                              <i class="fas fa-reply" aria-hidden="true"></i>
                            </span>
                          </a>
                          <a class="level-item" aria-label="retweet">
                            <span class="icon is-small">
                              <i class="fas fa-retweet" aria-hidden="true"></i>
                            </span>
                          </a>
                          <a class="level-item" aria-label="like">
                            <span class="icon is-small">
                              <i class="fas fa-heart" aria-hidden="true"></i>
                            </span>
                          </a>
                        </div>
                      </nav>
                    </div>
                  </article>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>
</template>

<script>
export default {
  name: 'FrontPage',
  props: {
    avatar: String
  }
}
</script>