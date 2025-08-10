
  const { createApp } = Vue

  createApp({

    data() {
      return {
        message_id: 0,
        message_body: "",
        comment_id: [],
        level: 0,
        message_com_id: "",
        ws_user: ""
      }
    },



    created() {
        this.ws_user = `user_ws_${Date.now()}`;
    },


    mounted() {

    },

    updated() {

    },


    watch: {

    },


    methods: {

       getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let cookie of cookies) {
                    cookie = cookie.trim();
                    if (cookie.startsWith(name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        },



        make_html_block_for_new_comment(res)
        {
            const comment_id = res.data.id;
            const comment_answer_id = this.message_id > 0 ? res.data.answer_id : 0;
            const id_block = this.message_id > 0 ? this.message_com_id : `added_new_comment`;
            const root_block = document.getElementById(id_block);

            const newElement = document.createElement('div');

            newElement.innerHTML = `
                <div class="card mb-2">
                    <div class="card-header bg-${this.message_id > 0 ? 'warning' : 'info'}">
                        <span class="me-2">
                            <i class="bi bi-person-circle me-1"></i>
                            <strong>${res.data.user}</strong> 
                        </span> 

                        <span class="me-2">
                            <small>${res.data.created_at}</small>
                        </span>

                        <span 
                            class="reply-btn"
                            data-bs-toggle="modal" 
                            data-bs-target="#staticBackdrop-add-comment"
                        > 
                            <i class="bi bi-reply"></i> ответить 
                        </span>
                    </div>

                    <div class="card-body">
                        <p class="card-text">${res.data.comment}</p>
                    </div>
                </div>
                `;

                newElement.id = `sub_comment_${comment_id}`;
                newElement.style = `margin-bottom: 10px; margin-left: ${this.level + 20}px`;


                newElement.querySelector('.reply-btn').addEventListener('click', () => {
                    this.answer_message(comment_id, 0);
                });

                root_block.parentNode.insertBefore(newElement, root_block.nextSibling);

                document.getElementById("send_comment_form").reset();
                this.message_body = "";

        },


        async submitForm()
        {
            const form = new FormData(document.getElementById('send_comment_form'));
            const csrftoken = this.getCookie('csrftoken');

            document.getElementById('send_comment_form_response').innerHTML = `
                <span class="text-success">
                    <span class="spinner-grow spinner-grow-sm me-1" role="status" aria-hidden="true"></span>
                    Ожидайте...
                </span>
            `;

            let response = await fetch(
                'send/', {
                    method: 'POST',
                    body: form
                }
            );

            let res = await response.json();


            if (res.status == "allow")
            {

                this.make_html_block_for_new_comment(res);
                
                if (this.message_id == 0)
                {
                    const comment_id = res.data.id;
                    const root_block = document.getElementById("added_new_comment");

                    const newElement = document.createElement('div');

                    newElement.innerHTML = `
                        <div class="card mb-2">
                            <div class="card-header bg-warning">
                                <span class="me-2">
                                    <i class="bi bi-person-circle me-1"></i>
                                    <strong>${res.data.user}</strong> 
                                </span> 

                                <span class="me-2">
                                    <small>${res.data.created_at}</small>
                                </span>

                                <span 
                                    class="reply-btn"
                                    data-bs-toggle="modal" 
                                    data-bs-target="#staticBackdrop-add-comment"
                                > 
                                    <i class="bi bi-reply"></i> ответить 
                                </span>
                            </div>

                            <div class="card-body">
                                <p class="card-text">${res.data.comment}</p>
                            </div>
                        </div>
                    `;

                    newElement.id = `comment_${comment_id}`;
                    newElement.style.border = '1px solid red; margin-bottom:20px;';

                    newElement.querySelector('.reply-btn').addEventListener('click', () => {
                        this.answer_message(comment_id, 0);
                    });

                    root_block.parentNode.insertBefore(newElement, root_block.nextSibling);

                    document.getElementById("send_comment_form").reset();
                    this.message_body = "";

                    this.make_html_block_for_new_comment(res);

                }
            }

            document.getElementById('send_comment_form_response').innerHTML = `${res.message}`;

        },



        answer_message(id, lvl, sub=0)
        {
            this.message_id = id;
            this.level = lvl;

            console.log(`Message ID: ${this.message_id}`);
            console.log(`sub: ${sub}`);

            this.message_com_id = sub == 0 ? `comment_${id}` : `sub_comment_${id}`;
        },


        cancel_answer()
        {
            this.message_id = 0;
            this.message_com_id = "";
        },


        add_tag(tag)
        {
            const text = prompt("Введите текст:");

            if (!text || text.trim() === "") return;

            const tags = {
                strong: `[b]${text}[/b] `,
                italic: `[i]${text}[/i] `,
                code: `[code]${text}[/code] `,
                link: `[a href="${text}"]${text}[/a] `
            };

            if (tags[tag])
            {
                this.message_body += tags[tag];
            }

        },


        fix_html_tags(text)
        {
            return text
                .replace(/\[b\](.*?)\[\/b\]/gi, '<strong>$1</strong>')
                .replace(/\[i\](.*?)\[\/i\]/gi, '<em>$1</em>')
                .replace(/\[code\](.*?)\[\/code\]/gi, '<pre><code>$1</code></pre>')
                .replace(/\[a href="(.*?)"\](.*?)\[\/a\]/gi, '<a href="$1">$2</a>');
        }


    }


  }).mount('#vue_app')