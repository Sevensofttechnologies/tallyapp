/**
 * Widgets Logic
 * Handles interactive elements for the Widgets Library
 */
(function (global) {

    // --- Chat Simulation ---
    class ChatWidget {
        constructor(element) {
            this.element = element;
            this.input = element.querySelector('.chat-input');
            this.body = element.querySelector('.chat-body');
            this.sendBtn = element.querySelector('.btn-send');

            this.sendBtn.addEventListener('click', () => this.send());
            this.input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.send();
            });

            // Scroll to bottom initially
            this.scrollToBottom();
        }

        send() {
            const text = this.input.value.trim();
            if (!text) return;

            this.addMessage(text, 'sent');
            this.input.value = '';

            // Auto Reply Simulation
            setTimeout(() => {
                this.addMessage("That sounds great! I'll update the ticket.", 'received');
            }, 1500);
        }

        addMessage(text, type) {
            const bubble = document.createElement('div');
            bubble.className = `chat-bubble ${type}`;
            bubble.textContent = text;
            this.body.appendChild(bubble);
            this.scrollToBottom();
        }

        scrollToBottom() {
            this.body.scrollTop = this.body.scrollHeight;
        }
    }

    // --- Live Stats Simulation ---
    function initStats() {
        setInterval(() => {
            document.querySelectorAll('[data-simulate="sales"]').forEach(el => {
                const current = parseInt(el.textContent.replace(/,/g, ''));
                const change = Math.floor(Math.random() * 10) - 2; // Bias upwards
                el.textContent = (current + change).toLocaleString();
            });
        }, 3000);
    }

    // --- Init ---
    document.addEventListener('DOMContentLoaded', () => {
        // Init Chats
        document.querySelectorAll('.chat-widget').forEach(el => new ChatWidget(el));

        // Init Live Stats
        initStats();
    });

})(window);
