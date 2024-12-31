window.onload = function() {
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function(message) {
        // 讓消息滑出
        setTimeout(function() {
            message.classList.add('flash-visible');
        }, 100);

        // 5秒後自動消失
        setTimeout(function() {
            message.classList.remove('flash-visible');
        }, 5100);
    });
};
