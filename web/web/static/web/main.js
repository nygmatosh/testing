
  const { createApp } = Vue

  createApp({

    data() {
      return {
        message_id: 0,
        message_body: "",
        comment_id: [],
        level: 0
      }
    },



    created() {

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

            document.getElementById('send_comment_form_response').innerHTML = `${res.message}`;

        },



        answer_message(id, lvl)
        {
            this.message_id = id;
            this.level = lvl;
            console.log(this.message_id);
            console.log(this.level);
        },


        cancel_answer()
        {
            this.message_id = 0;
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