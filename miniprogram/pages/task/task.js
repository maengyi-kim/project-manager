const api = require('../../utils/api');

Page({
  data: {
    isNew: false,
    projectId: null,
    parentId: null,
    taskId: null,
    task: {
      title: '',
      assignee: '',
      start_date: '',
      deadline: '',
      priority: 2,
      progress: 0,
      remark: '',
      status: 'todo',
    },
    newTitle: '',
    children: [],
  },

  onLoad(options) {
    const isNew = options.new === '1';
    this.setData({
      isNew,
      projectId: parseInt(options.projectId),
      parentId: options.parentId ? parseInt(options.parentId) : null,
    });

    if (!isNew && options.id) {
      this.setData({ taskId: parseInt(options.id) });
      this.loadTask();
    }
  },

  async loadTask() {
    // 从项目树中加载任务
    try {
      const tasks = await api.getTaskTree(this.data.projectId);
      const task = tasks.find(t => t.id === this.data.taskId);
      if (task) {
        // 加载子任务
        const children = tasks.filter(t => t.parent_id === this.data.taskId);
        // 计算当前任务的深度，限制最多子子任务
        const depth = this.calcTaskDepth(task.id, tasks);
        this.setData({ task, children, taskDepth: depth });
      }
    } catch (err) {
      wx.showToast({ title: '加载失败', icon: 'none' });
    }
  },

  // 计算单个任务的深度
  calcTaskDepth(id, tasks) {
    const map = {};
    tasks.forEach(t => map[t.id] = t);
    let d = 0, cur = map[id];
    while (cur && cur.parent_id) {
      d++;
      cur = map[cur.parent_id];
      if (!cur || d >= 2) break;
    }
    return d;
  },

  onTitleInput(e) {
    this.setData({ newTitle: e.detail.value });
  },

  onFieldChange(e) {
    const field = e.currentTarget.dataset.field;
    const value = e.detail.value;
    this.setData({ [`task.${field}`]: value });
  },

  onDateChange(e) {
    const field = e.currentTarget.dataset.field;
    const value = e.detail.value;
    this.setData({ [`task.${field}`]: value });
  },

  onSetPriority(e) {
    const p = parseInt(e.currentTarget.dataset.p);
    this.setData({ 'task.priority': p });
  },

  onProgressChange(e) {
    this.setData({ 'task.progress': e.detail.value });
  },

  onQuickProgress(e) {
    const p = parseInt(e.currentTarget.dataset.p);
    this.setData({ 'task.progress': p });
  },

  async onSave() {
    const { isNew, task, newTitle, projectId, parentId, taskId } = this.data;

    if (isNew) {
      if (!newTitle) {
        wx.showToast({ title: '请输入任务名称', icon: 'none' });
        return;
      }
      try {
        await api.createTask({
          project_id: projectId,
          parent_id: parentId || null,
          title: newTitle,
          assignee: task.assignee || '',
          start_date: task.start_date || null,
          deadline: task.deadline || null,
          priority: task.priority,
        });
        wx.showToast({ title: '创建成功', icon: 'success' });
        // 回到项目详情页，强制刷新
        setTimeout(() => {
          wx.redirectTo({ url: `/pages/project/project?id=${projectId}` });
        }, 500);
      } catch (err) {
        wx.showToast({ title: '创建失败', icon: 'none' });
      }
    } else {
      try {
        await api.updateTask(taskId, {
          title: task.title,
          assignee: task.assignee,
          start_date: task.start_date || null,
          deadline: task.deadline || null,
          priority: task.priority,
          progress: task.progress,
          remark: task.remark,
        });
        wx.showToast({ title: '保存成功', icon: 'success' });
        wx.navigateBack();
      } catch (err) {
        wx.showToast({ title: '保存失败', icon: 'none' });
      }
    }
  },

  onDelete() {
    wx.showModal({
      title: '确认删除',
      content: '子任务也会一起删除',
      success: (res) => {
        if (res.confirm) {
          api.deleteTask(this.data.taskId).then(() => {
            wx.navigateBack();
            wx.showToast({ title: '已删除', icon: 'success' });
          });
        }
      }
    });
  },

  onAddSubTask() {
    const { projectId, taskId } = this.data;
    wx.navigateTo({
      url: `/pages/task/task?projectId=${projectId}&parentId=${taskId}&new=1`
    });
  },

  onOpenChildTask(e) {
    const id = e.currentTarget.dataset.id;
    const { projectId } = this.data;
    wx.navigateTo({
      url: `/pages/task/task?id=${id}&projectId=${projectId}`
    });
  }
});
