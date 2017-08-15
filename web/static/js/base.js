function toggle_tab() {
    $('#search_tab').tab('show');
}

function toggle_register() {
    if(id === -1){
        $('#register_tool').modal('show')
    }
    else{
        alert("You have already login, please logout first !")
    }
}

function jump_group_management() {
    if(id === -1){
        alert("Please login first !");
        $('#login_tool').modal('show')
    }
    else{
        window.location.href = "/edit_groups/"
    }
}

Vue.conponent('navigation-bar', {
    template: `
    `
});


var navigation_bar = new Vue({
    el: 'nav_app',
    data: {
        id: id,
        name: name
    },
    methods: {
    }
});

var login_tool = new Vue({
    el: '#login_tool',
    data: {
        account: "",
        password: ""
    },
    methods: {
        login: function(){
            axios.post('/api/sessions/',
                {
                    "account": this.account,
                    "password": this.password
                }
            ).then(function(response){
                location.reload()
            }).catch(function(error){
                console.log(error);
                alert("Unmatched account and password !")
            })
        }
    }
});


var register_tool = new Vue({
    el: '#register_tool',
    data: {
        name: "",
        is_registered: "1",
        account: "",
        password: "",
        gs_link: "",
        invitation_code: ""
    },
    methods: {
        register: function(){
            axios.post('/api/authors/',
                {
                    'name': this.name,
                    'is_registered': this.is_registered,
                    'account': this.account,
                    'password': this.password,
                    'gs_link': this.gs_link,
                    'invitation_code': this.invitation_code
                }
            ).then(function (response){
                location.reload()
            }).catch(function(error){
                alert("Unknown server error !")
            })
        }
    }
});
window.onload = toggle_tab;

var logout_tool = new Vue({
    el: "#logout_tool",
    data: {
        id: id,
        name: name
    },
    methods: {
        logout: function(){
            axios.delete('/api/sessions/')
                .then(function(response){
                    location.reload()
                }).catch(function(error){
                alert("Unknown server error !")
            })
        }
    }
});



