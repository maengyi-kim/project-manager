const api = require('../../utils/api');

Page({
  data: {
    projectId: null,
    project: {},
    tasks: [],
    viewMode: 'list',       // list / gantt / simple

    // 甘特图数据
    ganttData: [],
    ganttHeaders: [],
    ganttTotalWidth: 0,
    dayWidth: 36,
    ganttProjectStart: null,
    ganttProjectEnd: null,

    // 简约时间数据
    simpleData: [],
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ projectId: parseInt(options.id) });
      this.loadProject();
    }
  },

  onShow() {
    if (this.data.projectId) this.loadProject();
  },

  async loadProject() {
    try {
      const project = await api.getProject(this.data.projectId);
      const rawTasks = project.tasks || [];
      // 前端自己计算每层缩进深度，不依赖后端 depth
      const tasks = this.calcDepth(rawTasks);
      this.setData({ project, tasks });

      // 加载甘特图数据
      this.loadGanttData();
      // 加载简约时间数据
      this.buildSimpleData(project.tasks);
    } catch (err) {
      wx.showToast({ title: '加载失败', icon: 'none' });
    }
  },

  // ====== 前端计算任务缩进深度 ======
  calcDepth(tasks) {
    const map = {};
    tasks.forEach(t => map[t.id] = t);

    function getDepth(id) {
      let d = 0;
      let cur = map[id];
      while (cur && cur.parent_id) {
        d++;
        cur = map[cur.parent_id];
        if (!cur) break;
        // 最大深度限制为 2（主任务-子任务-子子任务）
        if (d >= 2) break;
      }
      return d;
    }

    return tasks.map(t => ({
      ...t,
      depth: getDepth(t.id),
    }));
  },

  // ====== 甘特图 ======
  async loadGanttData() {
    try {
      const raw = await api.getGanttData(this.data.projectId);
      const p = raw.project;
      const tasks = raw.tasks || [];

      if (tasks.length === 0) {
        this.setData({ ganttData: [] });
        return;
      }

      // 找到所有任务的最早开始和最晚截止
      let minDate = null, maxDate = null;
      tasks.forEach(t => {
        if (t.start_date && (!minDate || t.start_date < minDate)) minDate = t.start_date;
        if (t.deadline && (!maxDate || t.deadline > maxDate)) maxDate = t.deadline;
      });

      const start = new Date(minDate);
      const end = new Date(maxDate);
      const totalDays = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1;

      // 生成日期头
      const dw = this.data.dayWidth;
      const headers = [];
      for (let i = 0; i < totalDays; i++) {
        const d = new Date(start);
        d.setDate(d.getDate() + i);
        headers.push({
          day: `${d.getMonth() + 1}/${d.getDate()}`,
          weekday: ['日','一','二','三','四','五','六'][d.getDay()],
        });
      }

      // 计算每条的 left/width
      const ganttData = tasks.map(t => {
        const tStart = t.start_date ? new Date(t.start_date) : start;
        const tEnd = t.deadline ? new Date(t.deadline) : end;
        const leftDays = Math.max(0, Math.ceil((tStart - start) / (1000 * 60 * 60 * 24)));
        const spanDays = Math.max(1, Math.ceil((tEnd - tStart) / (1000 * 60 * 60 * 24)) + 1);
        return {
          ...t,
          barLeft: leftDays * dw,
          barWidth: spanDays * dw,
        };
      });

      const totalWidth = Math.max(totalDays * dw + 200, 600);

      this.setData({
        ganttData,
        ganttHeaders: headers,
        ganttTotalWidth: totalWidth,
        ganttProjectStart: minDate,
        ganttProjectEnd: maxDate,
      });
    } catch (err) {
      console.error('甘特图加载失败:', err);
    }
  },

  zoomGantt(e) {
    const dir = e.currentTarget.dataset.dir;
    let dw = this.data.dayWidth;
    dw = dir === 'in' ? Math.min(dw + 6, 72) : Math.max(dw - 6, 18);
    this.setData({ dayWidth: dw });
    this.loadGanttData();
  },

  // ====== 简约时间 ======
  buildSimpleData(tasks) {
    // 过滤出有起止日期的任务
    const simple = tasks.filter(t => t.start_date || t.deadline);
    this.setData({ simpleData: simple });
  },

  // ====== 任务操作 ======
  taskDepth(task) {
    let depth = 0;
    // 粗略估计：从树中找父任务的嵌套深度
    return 0;
  },

  statusText(s) {
    const map = { active: '进行中', paused: '暂停', completed: '已完成', cancelled: '已取消',
                  todo: '待办', in_progress: '进行中' };
    return map[s] || s;
  },

  switchView(e) {
    const mode = e.currentTarget.dataset.mode;
    this.setData({ viewMode: mode });
  },

  onOpenTask(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: `/pages/task/task?id=${id}&projectId=${this.data.projectId}` });
  },

  onAddTask(e) {
    const parentId = e.currentTarget.dataset.pid;
    wx.navigateTo({
      url: `/pages/task/task?projectId=${this.data.projectId}&parentId=${parentId}&new=1`
    });
  },

  async onToggleStatus(e) {
    const id = e.currentTarget.dataset.id;
    const currentStatus = e.currentTarget.dataset.status;
    const newStatus = currentStatus === 'completed' ? 'in_progress' : 'completed';
    try {
      await api.updateTask(id, { status: newStatus });
      this.loadProject();
    } catch (err) {
      wx.showToast({ title: '更新失败', icon: 'none' });
    }
  },

  onShareProject() {
    const app = getApp();
    wx.setClipboardData({
      data: `${app.globalData.baseUrl}/share/${this.data.projectId}`,
      success: () => wx.showToast({ title: '链接已复制', icon: 'success' })
    });
  },

  onEditProject() {
    const p = this.data.project;
    wx.showModal({
      title: '编辑项目',
      content: '项目名称',
      editable: true,
      placeholderText: p.name,
      success: (res) => {
        if (res.confirm && res.content) {
          api.updateProject(this.data.projectId, { name: res.content }).then(() => this.loadProject());
        }
      }
    });
  },

  onDeleteProject() {
    wx.showModal({
      title: '确认删除',
      content: '删除后所有任务也会被删除，不可恢复',
      success: (res) => {
        if (res.confirm) {
          api.deleteProject(this.data.projectId).then(() => {
            wx.navigateBack();
            wx.showToast({ title: '已删除', icon: 'success' });
          });
        }
      }
    });
  }
});
