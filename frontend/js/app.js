// Global state
let currentPage = null;

// Load dashboard data
async function loadDashboard() {
    try {
        const pages = await API.getPages();
        document.getElementById('totalPages').textContent = pages.pages.length;
        
        let totalComments = 0;
        let totalReplies = 0;
        
        for (const page of pages.pages) {
            const stats = await API.getStats(page.page_id);
            totalComments += stats.total_comments_today || 0;
            totalReplies += stats.replied_today || 0;
        }
        
        document.getElementById('totalCommentsToday').textContent = totalComments;
        document.getElementById('totalRepliesToday').textContent = totalReplies;
        
        const replyRate = totalComments > 0 ? ((totalReplies / totalComments) * 100).toFixed(1) : 0;
        document.getElementById('replyRate').textContent = `${replyRate}%`;
        
        // Load recent activity
        loadRecentActivity(pages.pages);
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

async function loadRecentActivity(pages) {
    const container = document.getElementById('recentActivity');
    container.innerHTML = '';
    
    let allComments = [];
    
    for (const page of pages) {
        const comments = await API.getComments(page.page_id, 10);
        allComments.push(...comments.comments.map(c => ({...c, page_name: page.page_name})));
    }
    
    allComments.sort((a, b) => new Date(b.created_time) - new Date(a.created_time));
    allComments = allComments.slice(0, 20);
    
    if (allComments.length === 0) {
        container.innerHTML = '<p class="text-muted">No recent comments</p>';
        return;
    }
    
    const table = document.createElement('table');
    table.className = 'table table-sm';
    table.innerHTML = `
        <thead>
            <tr>
                <th>Page</th>
                <th>User</th>
                <th>Comment</th>
                <th>Time</th>
                <th>Replied</th>
            </tr>
        </thead>
        <tbody>
            ${allComments.map(comment => `
                <tr>
                    <td>${escapeHtml(comment.page_name)}</td>
                    <td>${escapeHtml(comment.user_name)}</td>
                    <td>${escapeHtml(comment.message.substring(0, 50))}${comment.message.length > 50 ? '...' : ''}</td>
                    <td>${new Date(comment.created_time).toLocaleString()}</td>
                    <td>${comment.replied ? '<i class="bi bi-check-circle-fill text-success"></i>' : '<i class="bi bi-hourglass-split text-warning"></i>'}</td>
                </tr>
            `).join('')}
        </tbody>
    `;
    
    container.appendChild(table);
}

// Load pages list
async function loadPages() {
    try {
        const result = await API.getPages();
        const pages = result.pages;
        const tbody = document.getElementById('pagesList');
        tbody.innerHTML = '';
        
        for (const page of pages) {
            const stats = await API.getStats(page.page_id);
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${escapeHtml(page.page_name)}</td>
                <td>${escapeHtml(page.category || 'N/A')}</td>
                <td>
                    <div class="form-check form-switch">
                        <input class="form-check-input" type="checkbox" 
                            ${page.auto_reply_enabled ? 'checked' : ''}
                            onchange="toggleAutoReply('${page.page_id}', this.checked)">
                    </div>
                </td>
                <td>${page.replies_count_today || 0}</td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="removePage('${page.page_id}')">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            `;
        }
        
        // Update page selects
        const commentSelect = document.getElementById('commentPageSelect');
        const templateSelect = document.getElementById('templatePageSelect');
        
        commentSelect.innerHTML = '<option value="">Select a page</option>';
        templateSelect.innerHTML = '<option value="">Select a page</option>';
        
        pages.forEach(page => {
            commentSelect.innerHTML += `<option value="${page.page_id}">${escapeHtml(page.page_name)}</option>`;
            templateSelect.innerHTML += `<option value="${page.page_id}">${escapeHtml(page.page_name)}</option>`;
        });
        
    } catch (error) {
        console.error('Error loading pages:', error);
    }
}

// Load comments for a page
async function loadComments(pageId) {
    try {
        const result = await API.getComments(pageId);
        const comments = result.comments;
        const container = document.getElementById('commentsList');
        
        if (comments.length === 0) {
            container.innerHTML = '<div class="alert alert-info">No comments found</div>';
            return;
        }
        
        const html = `
            <div class="list-group">
                ${comments.map(comment => `
                    <div class="list-group-item">
                        <div class="d-flex w-100 justify-content-between">
                            <h6 class="mb-1">${escapeHtml(comment.user_name)}</h6>
                            <small>${new Date(comment.created_time).toLocaleString()}</small>
                        </div>
                        <p class="mb-1">${escapeHtml(comment.message)}</p>
                        ${comment.replied ? `
                            <small class="text-success">
                                <i class="bi bi-reply"></i> Replied: ${escapeHtml(comment.reply_message)}
                            </small>
                        ` : '<span class="badge bg-warning">Pending reply</span>'}
                    </div>
                `).join('')}
            </div>
        `;
        
        container.innerHTML = html;
        
    } catch (error) {
        console.error('Error loading comments:', error);
        document.getElementById('commentsList').innerHTML = '<div class="alert alert-danger">Error loading comments</div>';
    }
}

// Load templates for a page
async function loadTemplates(pageId) {
    try {
        const result = await API.getTemplates(pageId);
        const templates = result.templates;
        const container = document.getElementById('templatesList');
        
        if (templates.length === 0) {
            container.innerHTML = '<div class="alert alert-info">No templates found. Click "Add Template" to create one.</div>';
            return;
        }
        
        const html = `
            <div class="list-group">
                ${templates.map(template => `
                    <div class="list-group-item">
                        <div class="d-flex w-100 justify-content-between">
                            <h6 class="mb-1">
                                <span class="badge bg-primary">${template.template_type}</span>
                                ${template.is_active ? '<span class="badge bg-success">Active</span>' : '<span class="badge bg-secondary">Inactive</span>'}
                            </h6>
                            <button class="btn btn-sm btn-danger" onclick="deleteTemplate('${template._id}')">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                        <p class="mt-2">${escapeHtml(template.content)}</p>
                        ${template.keywords && template.keywords.length > 0 ? `
                            <small class="text-muted">Keywords: ${template.keywords.join(', ')}</small>
                        ` : ''}
                    </div>
                `).join('')}
            </div>
        `;
        
        container.innerHTML = html;
        
    } catch (error) {
        console.error('Error loading templates:', error);
        document.getElementById('templatesList').innerHTML = '<div class="alert alert-danger">Error loading templates</div>';
    }
}

// Event handlers
async function toggleAutoReply(pageId, enabled) {
    try {
        await API.toggleAutoReply(pageId, enabled);
        showToast(`Auto reply ${enabled ? 'enabled' : 'disabled'}`, 'success');
    } catch (error) {
        console.error('Error toggling auto reply:', error);
        showToast('Error toggling auto reply', 'danger');
    }
}

async function removePage(pageId) {
    if (!confirm('Are you sure you want to remove this page?')) return;
    
    try {
        await API.removePage(pageId);
        showToast('Page removed successfully', 'success');
        loadPages();
        loadDashboard();
    } catch (error) {
        console.error('Error removing page:', error);
        showToast('Error removing page', 'danger');
    }
}

async function deleteTemplate(templateId) {
    if (!confirm('Are you sure you want to delete this template?')) return;
    
    try {
        await API.deleteTemplate(templateId);
        showToast('Template deleted successfully', 'success');
        const pageId = document.getElementById('templatePageSelect').value;
        if (pageId) loadTemplates(pageId);
    } catch (error) {
        console.error('Error deleting template:', error);
        showToast('Error deleting template', 'danger');
    }
}

// Form handlers
document.getElementById('addPageForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = {
        page_id: formData.get('page_id'),
        access_token: formData.get('access_token')
    };
    
    try {
        await API.addPage(data);
        showToast('Page added successfully', 'success');
        bootstrap.Modal.getInstance(document.getElementById('addPageModal')).hide();
        e.target.reset();
        loadPages();
        loadDashboard();
    } catch (error) {
        console.error('Error adding page:', error);
        showToast(error.message || 'Error adding page', 'danger');
    }
});

document.getElementById('addTemplateForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const pageId = document.getElementById('templatePageSelect').value;
    if (!pageId) {
        showToast('Please select a page first', 'warning');
        return;
    }
    
    const formData = new FormData(e.target);
    const data = {
        template_type: formData.get('template_type'),
        content: formData.get('content'),
        keywords: formData.get('keywords') ? formData.get('keywords').split(',') : []
    };
    
    try {
        await API.addTemplate(pageId, data);
        showToast('Template added successfully', 'success');
        bootstrap.Modal.getInstance(document.getElementById('addTemplateModal')).hide();
        e.target.reset();
        loadTemplates(pageId);
    } catch (error) {
        console.error('Error adding template:', error);
        showToast(error.message || 'Error adding template', 'danger');
    }
});

document.getElementById('commentPageSelect').addEventListener('change', (e) => {
    if (e.target.value) {
        loadComments(e.target.value);
    }
});

document.getElementById('templatePageSelect').addEventListener('change', (e) => {
    if (e.target.value) {
        loadTemplates(e.target.value);
    }
});

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showToast(message, type = 'info') {
    // Simple toast implementation
    const toastContainer = document.createElement('div');
    toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
    toastContainer.style.zIndex = '11';
    
    const toast = document.createElement('div');
    toast.className = `toast show bg-${type} text-white`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="toast-body">
            ${message}
            <button type="button" class="btn-close btn-close-white float-end" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    document.body.appendChild(toastContainer);
    
    setTimeout(() => {
        toastContainer.remove();
    }, 3000);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
    loadPages();
    
    // Auto refresh every 30 seconds
    setInterval(() => {
        if (document.querySelector('#dashboard-tab').classList.contains('active')) {
            loadDashboard();
        } else if (document.querySelector('#pages-tab').classList.contains('active')) {
            loadPages();
        } else if (document.querySelector('#comments-tab').classList.contains('active')) {
            const pageId = document.getElementById('commentPageSelect').value;
            if (pageId) loadComments(pageId);
        }
    }, 30000);
});
