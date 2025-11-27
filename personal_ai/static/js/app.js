// Personal AI Web App JavaScript

class PersonalAIApp {
    constructor() {
        this.chatInput = document.getElementById('chat-input');
        this.sendBtn = document.getElementById('send-btn');
        this.chatMessages = document.getElementById('chat-messages');
        
        // Initialize
        this.setupEventListeners();
        this.loadInitialData();
        
        // Focus input
        this.chatInput.focus();
    }

    setupEventListeners() {
        // Send message
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Modals
        this.setupModals();
    }

    setupModals() {
        // Task modal
        const taskModal = document.getElementById('task-modal');
        const addTaskBtn = document.getElementById('add-task-btn');
        const saveTaskBtn = document.getElementById('save-task-btn');
        const taskDescription = document.getElementById('task-description');

        addTaskBtn.addEventListener('click', () => {
            taskModal.style.display = 'block';
            taskDescription.focus();
        });

        saveTaskBtn.addEventListener('click', async () => {
            const description = taskDescription.value.trim();
            if (description) {
                await this.addTask(description);
                taskDescription.value = '';
                taskModal.style.display = 'none';
            }
        });

        // Profile modal
        const profileModal = document.getElementById('profile-modal');
        const addProfileBtn = document.getElementById('add-profile-btn');
        const saveProfileBtn = document.getElementById('save-profile-btn');
        const profileKey = document.getElementById('profile-key');
        const profileValue = document.getElementById('profile-value');

        addProfileBtn.addEventListener('click', () => {
            profileModal.style.display = 'block';
            profileKey.focus();
        });

        saveProfileBtn.addEventListener('click', async () => {
            const key = profileKey.value.trim();
            const value = profileValue.value.trim();
            if (key && value) {
                await this.updateProfile(key, value);
                profileKey.value = '';
                profileValue.value = '';
                profileModal.style.display = 'none';
            }
        });

        // Reflection modal
        const reflectionModal = document.getElementById('reflection-modal');
        const addReflectionBtn = document.getElementById('add-reflection-btn');
        const saveReflectionBtn = document.getElementById('save-reflection-btn');
        const reflectionNote = document.getElementById('reflection-note');

        addReflectionBtn.addEventListener('click', () => {
            reflectionModal.style.display = 'block';
            reflectionNote.focus();
        });

        saveReflectionBtn.addEventListener('click', async () => {
            const note = reflectionNote.value.trim();
            if (note) {
                await this.addReflection(note);
                reflectionNote.value = '';
                reflectionModal.style.display = 'none';
            }
        });

        // Close modals
        document.querySelectorAll('.close').forEach(closeBtn => {
            closeBtn.addEventListener('click', (e) => {
                e.target.closest('.modal').style.display = 'none';
            });
        });

        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                e.target.style.display = 'none';
            }
        });
    }

    async sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message) return;

        // Add user message to UI
        this.addMessageToUI('user', message);
        this.chatInput.value = '';
        this.setLoading(true);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message }),
            });

            const data = await response.json();
            
            if (response.ok) {
                this.addMessageToUI('assistant', data.response);
                // Reload tasks if command was task-related
                if (message.startsWith('/addtask') || message.startsWith('/tasks') || message.startsWith('/donetask')) {
                    await this.loadTasks();
                }
                if (message.startsWith('/profile')) {
                    await this.loadProfile();
                }
                if (message.startsWith('/reflect')) {
                    await this.loadReflections();
                }
            } else {
                this.addMessageToUI('assistant', `Error: ${data.error || 'Unknown error'}`);
            }
        } catch (error) {
            this.addMessageToUI('assistant', `Error: ${error.message}`);
        } finally {
            this.setLoading(false);
        }
    }

    addMessageToUI(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = role === 'user' ? 'You' : 'AI';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Simple markdown parsing (basic support)
        contentDiv.innerHTML = this.formatMessage(content);
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);
        
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    formatMessage(text) {
        // Basic markdown-like formatting
        let html = text
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>');
        
        // Convert URLs to links
        html = html.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
        
        return html;
    }

    setLoading(isLoading) {
        this.sendBtn.disabled = isLoading;
        if (isLoading) {
            this.sendBtn.innerHTML = '<span class="loading"></span>';
        } else {
            this.sendBtn.textContent = 'Send';
        }
    }

    async loadInitialData() {
        await Promise.all([
            this.loadConversation(),
            this.loadTasks(),
            this.loadProfile(),
            this.loadReflections(),
        ]);
    }

    async loadConversation() {
        try {
            const response = await fetch('/api/conversation');
            const data = await response.json();
            
            if (response.ok) {
                data.messages.forEach(msg => {
                    this.addMessageToUI(msg.role, msg.content);
                });
            }
        } catch (error) {
            console.error('Error loading conversation:', error);
        }
    }

    async loadTasks() {
        try {
            const response = await fetch('/api/tasks');
            const data = await response.json();
            
            if (response.ok) {
                const tasksList = document.getElementById('tasks-list');
                tasksList.innerHTML = '';
                
                if (data.tasks.length === 0) {
                    tasksList.innerHTML = '<p style="color: var(--text-secondary); font-size: 0.9rem;">No tasks yet</p>';
                } else {
                    data.tasks.forEach(task => {
                        const taskItem = document.createElement('div');
                        taskItem.className = `task-item ${task.status}`;
                        
                        const description = document.createElement('span');
                        description.className = 'task-description';
                        description.textContent = task.description;
                        
                        const status = document.createElement('span');
                        status.className = `task-status ${task.status}`;
                        status.textContent = task.status;
                        
                        const actions = document.createElement('div');
                        if (task.status === 'open') {
                            const doneBtn = document.createElement('button');
                            doneBtn.textContent = '✓';
                            doneBtn.style.cssText = 'background: var(--success-color); color: white; border: none; padding: 0.25rem 0.5rem; border-radius: 4px; cursor: pointer; font-size: 0.8rem;';
                            doneBtn.addEventListener('click', () => this.completeTask(task.id));
                            actions.appendChild(doneBtn);
                        }
                        
                        taskItem.appendChild(description);
                        taskItem.appendChild(status);
                        if (actions.children.length > 0) {
                            taskItem.appendChild(actions);
                        }
                        
                        tasksList.appendChild(taskItem);
                    });
                }
            }
        } catch (error) {
            console.error('Error loading tasks:', error);
        }
    }

    async addTask(description) {
        try {
            const response = await fetch('/api/tasks', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ description }),
            });

            if (response.ok) {
                await this.loadTasks();
            } else {
                const data = await response.json();
                alert(`Error: ${data.error || 'Failed to add task'}`);
            }
        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    }

    async completeTask(taskId) {
        try {
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ status: 'done' }),
            });

            if (response.ok) {
                await this.loadTasks();
            } else {
                const data = await response.json();
                alert(`Error: ${data.error || 'Failed to complete task'}`);
            }
        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    }

    async loadProfile() {
        try {
            const response = await fetch('/api/profile');
            const data = await response.json();
            
            if (response.ok) {
                const profileList = document.getElementById('profile-list');
                profileList.innerHTML = '';
                
                if (Object.keys(data.profile).length === 0) {
                    profileList.innerHTML = '<p style="color: var(--text-secondary); font-size: 0.9rem;">No profile info yet</p>';
                } else {
                    Object.entries(data.profile).forEach(([key, value]) => {
                        const profileItem = document.createElement('div');
                        profileItem.className = 'profile-item';
                        profileItem.innerHTML = `<strong>${key}:</strong> ${value}`;
                        profileList.appendChild(profileItem);
                    });
                }
            }
        } catch (error) {
            console.error('Error loading profile:', error);
        }
    }

    async updateProfile(key, value) {
        try {
            const response = await fetch('/api/profile', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ key, value }),
            });

            if (response.ok) {
                await this.loadProfile();
            } else {
                const data = await response.json();
                alert(`Error: ${data.error || 'Failed to update profile'}`);
            }
        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    }

    async loadReflections() {
        try {
            const response = await fetch('/api/reflections');
            const data = await response.json();
            
            if (response.ok) {
                const reflectionsList = document.getElementById('reflections-list');
                reflectionsList.innerHTML = '';
                
                if (data.reflections.length === 0) {
                    reflectionsList.innerHTML = '<p style="color: var(--text-secondary); font-size: 0.9rem;">No reflections yet</p>';
                } else {
                    data.reflections.slice(-5).reverse().forEach(reflection => {
                        const reflectionItem = document.createElement('div');
                        reflectionItem.className = 'reflection-item';
                        reflectionItem.textContent = reflection;
                        reflectionsList.appendChild(reflectionItem);
                    });
                }
            }
        } catch (error) {
            console.error('Error loading reflections:', error);
        }
    }

    async addReflection(note) {
        try {
            const response = await fetch('/api/reflections', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ note }),
            });

            if (response.ok) {
                await this.loadReflections();
            } else {
                const data = await response.json();
                alert(`Error: ${data.error || 'Failed to add reflection'}`);
            }
        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new PersonalAIApp();
});

