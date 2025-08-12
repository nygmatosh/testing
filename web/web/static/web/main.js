
  const { createApp } = Vue

  createApp({

    data() {
      return {
        message_id: 0,
        message_body: "",
        comment_id: [],
        level: 0,
        message_com_id: "",
        ws_user: "",
      }
    },



    created() {
        this.ws_user = `user_ws_${Date.now()}`;

        const socket = new WebSocket(`ws://${location.host}:8001/?username=${this.ws_user}`);

        socket.onopen = () => {
            console.log('WS connected');
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('Полученный JSON:', data);

            if ("status" in data)
            {
                const icon = this.response_status_icon(data);
                
                const response_text = data.status == "allow" ? "Комментарий успешно добавлен" : "Ошибка при добавлении комментария";
                const text_style = data.status == "allow" ? "text-success" : "text-danger";

                if (data.status == "allow")
                {
                    this.make_html_block_for_new_comment(data);
                }

                document.getElementById("send_comment_form_response").innerHTML = `
                    <span class='${text_style}'> 
                        ${icon} <strong>${response_text}</strong> 
                    </span>
                `;
            }

        };

        socket.onerror = (error) => {
            console.error('WS error', error);
        };

        socket.onclose = () => {
            console.log('WS disconnected');
        };

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



        response_status_icon(res)
        {
            return res.status == "allow" ? "🟢" : "🔴";
        },


        
        make_html_block_for_new_comment(res)
        {
            const comment_id = res.id; //res.data.id;
            const id_block = this.message_id > 0 ? this.message_com_id : `added_new_comment`;
            const new_block_id = this.message_id > 0 ? `sub_comment_${comment_id}` : `comment_${comment_id}`;
            const root_block = document.getElementById(id_block);

            const file_block = res.file.length > 0 
            ? 
            `
                <div class="mt-1 mb-1">
                    <a 
                        href="media/${res.file}"
                        data-lightbox="gallery1"
                        data-title="${this.fix_html_tags(res.comment)}"
                    >
                        <img 
                            src="media/${res.file}"
                            style="width:150px;"
                        >
                    </a>
                </div>
            ` 
            : 
            "";

            const newElement = document.createElement('div');

            newElement.innerHTML = `
                <div class="card mb-2">
                    <div class="card-header bg-${this.message_id == 0 ? 'warning' : 'info'}">
                        <span class="me-2">
                            <i class="bi bi-person-circle me-1"></i>
                            <strong>${res.user}</strong> 
                        </span> 

                        <span class="me-2">
                            <small>${res.created_at}</small>
                        </span>

                        <span 
                            class="reply-btn"
                            data-bs-toggle="modal" 
                            data-bs-target="#staticBackdrop-add-comment"
                            style="cursor: pointer;"
                        > 
                            <i class="bi bi-reply"></i> ответить 
                        </span>
                    </div>

                    <div class="card-body">
                        <p> ${this.fix_html_tags(res.comment)} </p>
                        ${file_block}
                    </div>
                </div>
                `;

                const level_size = this.message_id > 0 ? this.level + 20 : this.level;

                newElement.id = new_block_id;
                newElement.style = `margin-bottom: 10px; margin-left: ${level_size}px`;

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

            const icon = this.response_status_icon(res);

            document.getElementById('send_comment_form_response').innerHTML = `
                <span class="text-info"> 
                    ${icon} ${res.message} 
                </span>
            `;

        },



        answer_message(id, lvl, sub=0)
        {
            this.message_id = id;
            this.level = lvl;

            console.log(`Message ID: ${this.message_id}`);
            console.log(`sub: ${sub}`);

            this.message_com_id = sub == 0 ? `comment_${id}` : `sub_comment_${id}`;
            document.getElementById("send_comment_form_response").innerHTML = "";
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