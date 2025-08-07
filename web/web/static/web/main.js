
  const { createApp } = Vue

  createApp({

    data() {
      return {

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
                    body: form,
                    headers:
                    {
                        'X-CSRFToken': csrftoken
                    }
                }
            );

            let res = await response.json();

            document.getElementById('send_comment_form_response').innerHTML = "";

        }

    }


  }).mount('#vue_app')