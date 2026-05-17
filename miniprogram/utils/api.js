const app = getApp();

const request = (url, method = 'GET', data = {}) => {
  return new Promise((resolve, reject) => {
    const baseUrl = app.globalData.baseUrl;
    wx.request({
      url: baseUrl + url,
      method,
      data,
      header: { 'Content-Type': 'application/json' },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else {
          wx.showToast({ title: res.data?.error || '请求失败', icon: 'none' });
          reject(res.data);
        }
      },
      fail: (err) => {
        wx.showToast({ title: '网络异常', icon: 'none' });
        reject(err);
      }
    });
  });
};

module.exports = {
  // 项目
  getProjects: () => request('/api/projects'),
  getProject: (id) => request(`/api/projects/${id}`),
  createProject: (data) => request('/api/projects', 'POST', data),
  updateProject: (id, data) => request(`/api/projects/${id}`, 'PUT', data),
  deleteProject: (id) => request(`/api/projects/${id}`, 'DELETE'),
  shareProject: (id) => request(`/api/projects/${id}/share`),

  // 任务
  getTaskTree: (projectId) => request(`/api/tasks/tree/${projectId}`),
  getGanttData: (projectId) => request(`/api/tasks/gantt/${projectId}`),
  createTask: (data) => request('/api/tasks', 'POST', data),
  updateTask: (id, data) => request(`/api/tasks/${id}`, 'PUT', data),
  deleteTask: (id) => request(`/api/tasks/${id}`, 'DELETE'),

  // 统计
  getOverview: () => request('/api/stats/overview'),
};
