$(document).ready(function () {
    var ENTER_KEY = 13;

    $(document).ajaxError(function (event, request) {
        var message = null;

        if (request.responseJSON && request.responseJSON.hasOwnProperty('message')) {
            message = request.responseJSON.message;
        } else if (request.responseText) {
            var IS_JSON = true;
            try {
                var data = JSON.parse(request.responseText);
            }
            catch (err) {
                IS_JSON = false;
            }

            if (IS_JSON && data !== undefined && data.hasOwnProperty('message')) {
                message = JSON.parse(request.responseText).message;
            } else {
                message = default_error_message;
            }
        } else {
            message = default_error_message;
        }
        M.toast({html: message});
    });

    function activeM() {
        $('.sidenav').sidenav();
        $('ul.tabs').tabs();
        $('.modal').modal();
        $('.tooltipped').tooltip();
        $('.dropdown-trigger').dropdown({
                constrainWidth: false,
                coverTrigger: false
            }
        );
        $(".button-collapse").sideNav('show');
    }
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader('X-CSRFToken', csrf_token);
            }
        }
    });
    // Bind a callback that executes when document.location.hash changes.
    $(window).bind('hashchange', function () {
        // Some browers return the hash symbol, and some don't.
        var hash = window.location.hash.replace('#', '');
        var url = null;
        if (hash === 'login') {
            url = login_page_url
        } else if (hash === 'app') {
            url = app_page_url
        } else {
            url = intro_page_url
        }

        $.ajax({
            type: 'GET',
            url: url,
            success: function (data) {
                $('#main').hide().html(data).fadeIn(800);
                activeM();

            }
        });
    });

    if (window.location.hash === '') {
        window.location.hash = '#intro'; 
    } else {
        $(window).trigger('hashchange');
    }
    if (window.location.hash === 'app') {
        $('main').css('padding-left','300px')
    }

    function register(){
        var username = $('#username-input').val();
        var password = $('#password-input').val();
        if(!username || !password){
            M.toast({html: register_error_message});
            return;
        }
        var data = {
            'username': username,
            'password': password
        };
        $.ajax({
            type: 'POST',
            url: register_url,
            data: JSON.stringify(data),
            contentType: 'application/json;charset=UTF-8',
            success: function (data) {
                if (window.location.hash === '#app' || window.location.hash === 'app') {
                    $(window).trigger('hashchange');
                } else {
                    window.location.hash = '#app';
                }
                activeM();
                M.toast({html: data.message});
            }
        });
    }
    $(document).on('click', '#register-btn', register);

    function login_user(){
        var username = $('#username-input').val();
        var password = $('#password-input').val();
        if(!username || !password){
            M.toast({html: login_error_message});
            return;
        }
        var data = {
            'username': username,
            'password': password
        };
        $.ajax({
            type: 'POST',
            url: login_url,
            data: JSON.stringify(data),
            contentType: 'application/json;charset=UTF-8',
            success: function (data) {
                if (window.location.hash === '#app' || window.location.hash === 'app') {
                    $(window).trigger('hashchange');
                } else {
                    window.location.hash = '#app';
                }
                activeM();
                M.toast({html: data.message});
            }
        });
    }

    $(document).on('keyup', function (e) {
        if (e.which === ENTER_KEY) {
            login_user();
        }
    });

    $(document).on('click', '#login-btn', login_user);

    $(document).on('click', '#logout-btn', function(){
        $.ajax({
            type: 'GET',
            url: logout_url,
            success: function() {
                window.location.hash = '#intro';
                activeM();
                M.toast({html: data.message});
            }
        });
    });

    $(document).on('click', '#active-todo', function () {
        var $todo_list = $('.todo');
        $todo_list.show();
        $todo_list.filter(function(){
            return $(this).data('done');
        }).hide();
    });

    $(document).on('click', '#all-todo', function(){
        $('.todo').show();
    });

    $(document).on('click', '#completed-todo', function(){
        var $todo_list = $('.todo');
        $todo_list.show();
        $todo_list.filter(function(){
            return !$(this).data('done');
        }).hide();
    });

    $(document).on('click', '.label', function(){
        $.ajax({
            type: 'GET',
            url: $(this).data('href'),
            success: function(data){
                $('.todos').hide().html(data.html).fadeIn(800);
                activeM();
                refresh_count();
            }
        });
    });

    function refresh_count() {
        var $todos = $('.todo');

        var all_count = $todos.length;
        var active_count = $todos.filter(function () {
            return $(this).data('done') === false;
        }).length;
        var completed_count = $todos.filter(function () {
            return $(this).data('done') === true;
        }).length;
        $('#all-count').html(all_count);
        $('#active-count').html(active_count);
        $('#completed-count').html(completed_count);
    }

    function refresh_nav(){
        $.ajax({
            type: 'GET',
            url: refresh_nav_url,
            success: function(data){
                $('#side-nav').hide().html(data.html).fadeIn(800);
                activeM();
            }
        });

    }

    function new_todo(){
        var body = $('#body-input').val().trim();
        var label = $('#label-input').val().trim();
        if(!body || !label)
        {
            M.toast({html: " Empty Body or Label "});
            return;
        }

        $('#body-input').focus().val('');
        $('#label-input').val('');
        var data = {
            'body': body,
            'label': label
        };
        $.ajax({
            type: 'POST',
            url: new_todo_url,
            data: JSON.stringify(data),
            contentType: 'application/json;charset=UTF-8',
            success: function(data){
                M.toast({html: data.message, classes: 'rounded'});
                $('.todos').append(data.html);
                activeM();
                refresh_count();
                refresh_nav();
            }
        });
    }
    $(document).on('click','#new-todo-btn', new_todo);

    $(document).on('click', '.delete-btn', function(){
        var $todo = $(this).parent().parent();
        
        $.ajax({
            type: 'DELETE',
            url: $(this).data('href'),
            success: function(data){
                $todo.remove();
                activeM();
                refresh_count();
                refresh_nav();
                M.toast({html: data.message})
            }
        });
    });

    $(document).on('click','.done-btn', function(){
        var $todo= $(this).parent().parent();
        var $this = $(this);

        if($todo.data('done')){
            $.ajax({
                type: 'PATCH',
                url: $this.data('href'),
                success: function(data) {
                    $this.next().removeClass('inactive-todo');
                    $this.next().addClass('active-item');
                    $this.find('i').text('check_box_outline_blank');
                    $todo.data('done', false);
                    M.toast({html: data.message});
                    refresh_count();
                }
            })
        }else{
            $.ajax({
                type: 'PATCH',
                url: $this.data('href'),
                success: function (data) {
                    $this.next().removeClass('active-item');
                    $this.next().addClass('inactive-item');
                    $this.find('i').text('check_box');
                    $todo.data('done', true);
                    M.toast({html: data.message});
                    refresh_count();
                }
            })
        }
    });

    activeM()
});
