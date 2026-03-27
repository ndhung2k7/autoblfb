const API_BASE = 'http://localhost:8000/api';

class API {
    static async request(endpoint, method = 'GET', data = null) {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        try {
            const response = await fetch(`${API_BASE}${endpoint}`, options);
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.detail || 'API request failed');
            }
            
            return result;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
    
    // Pages
    static async getPages() {
        return this.request('/pages/list');
    }
    
    static async addPage(pageData) {
        return this.request('/pages/add', 'POST', pageData);
    }
    
    static async toggleAutoReply(pageId, enabled) {
        return this.request(`/pages/${pageId}/toggle-reply?enabled=${enabled}`, 'PUT');
    }
    
    static async removePage(pageId) {
        return this.request(`/pages/${pageId}`, 'DELETE');
    }
    
    // Comments
    static async getComments(pageId, limit = 50, replied = null) {
        let url = `/comments/${pageId}?limit=${limit}`;
        if (replied !== null) {
            url += `&replied=${replied}`;
        }
        return this.request(url);
    }
    
    static async getStats(pageId) {
        return this.request(`/comments/stats/${pageId}`);
    }
    
    // Templates
    static async getTemplates(pageId) {
        return this.request(`/templates/${pageId}`);
    }
    
    static async addTemplate(pageId, templateData) {
        return this.request(`/templates/${pageId}`, 'POST', templateData);
    }
    
    static async updateTemplate(templateId, templateData) {
        return this.request(`/templates/${templateId}`, 'PUT', templateData);
    }
    
    static async deleteTemplate(templateId) {
        return this.request(`/templates/${templateId}`, 'DELETE');
    }
}
