// pages/form/form.js
const app = getApp()

Page({
  data: {
    name: '',
    wechat_id: '',
    gender: '',
    check_in: '',
    check_out: '',
    smoking: '',
    schedule: '',
    noise_in: '',
    noise_out: '',
    user_agreement: false,
    privacy_agreement: false,
    group_code: '',
    today: '' // 今天的日期，用于限制picker
  },

  onLoad(options) {
    // 设置今天的日期
    const today = new Date()
    const year = today.getFullYear()
    const month = String(today.getMonth() + 1).padStart(2, '0')
    const day = String(today.getDate()).padStart(2, '0')

    this.setData({
      group_code: app.globalData.groupCode,
      today: `${year}-${month}-${day}`
    })
  },

  onNameInput(e) {
    this.setData({ name: e.detail.value })
  },

  onWechatInput(e) {
    // 只允许英文、数字、下划线和短横线
    const value = e.detail.value.replace(/[^a-zA-Z0-9_-]/g, '')
    this.setData({ wechat_id: value })
  },

  onGenderChange(e) {
    this.setData({ gender: e.detail.value })
  },

  onCheckInChange(e) {
    this.setData({ check_in: e.detail.value })
  },

  onCheckOutChange(e) {
    const check_out = e.detail.value
    const { check_in } = this.data

    // 如果已经选择了入住日期，立即验证
    if (check_in && check_out <= check_in) {
      wx.showToast({
        title: '退房日期必须晚于入住日期',
        icon: 'none',
        duration: 2000
      })
      // 不保存错误的日期
      return
    }

    this.setData({ check_out })
  },

  onSmokingChange(e) {
    this.setData({ smoking: e.detail.value })
  },

  onScheduleChange(e) {
    this.setData({ schedule: e.detail.value })
  },

  onNoiseInChange(e) {
    this.setData({ noise_in: e.detail.value })
  },

  onNoiseOutChange(e) {
    this.setData({ noise_out: e.detail.value })
  },

  onUserAgreementChange(e) {
    this.setData({ user_agreement: e.detail.value.length > 0 })
  },

  onPrivacyAgreementChange(e) {
    this.setData({ privacy_agreement: e.detail.value.length > 0 })
  },

  // 查看用户协议
  onViewUserAgreement() {
    wx.navigateTo({
      url: '/pages/agreement/agreement?type=user'
    })
  },

  // 查看隐私政策
  onViewPrivacyPolicy() {
    wx.navigateTo({
      url: '/pages/agreement/agreement?type=privacy'
    })
  },

  onSubmit() {
    const { name, wechat_id, gender, check_in, check_out, smoking, schedule, noise_in, noise_out, user_agreement, privacy_agreement, group_code } = this.data

    // 验证必填项
    if (!name) {
      wx.showToast({ title: '请输入姓名', icon: 'none' })
      return
    }
    if (!wechat_id) {
      wx.showToast({ title: '请输入微信号', icon: 'none' })
      return
    }
    if (!gender) {
      wx.showToast({ title: '请选择性别', icon: 'none' })
      return
    }
    if (!check_in) {
      wx.showToast({ title: '请选择入住日期', icon: 'none' })
      return
    }
    if (!check_out) {
      wx.showToast({ title: '请选择退房日期', icon: 'none' })
      return
    }
    // 验证日期逻辑
    if (check_out <= check_in) {
      wx.showToast({ title: '退房日期必须晚于入住日期', icon: 'none' })
      return
    }
    if (!smoking) {
      wx.showToast({ title: '请选择是否吸烟', icon: 'none' })
      return
    }
    if (!schedule) {
      wx.showToast({ title: '请选择作息习惯', icon: 'none' })
      return
    }
    if (!noise_in) {
      wx.showToast({ title: '请选择噪音容忍度', icon: 'none' })
      return
    }
    if (!noise_out) {
      wx.showToast({ title: '请选择噪音输出', icon: 'none' })
      return
    }
    if (!user_agreement || !privacy_agreement) {
      wx.showToast({ title: '请阅读并同意用户协议和隐私政策', icon: 'none' })
      return
    }

    // 提交数据
    wx.showLoading({ title: '提交中...' })

    wx.request({
      url: `${app.globalData.apiUrl}/api/submit`,
      method: 'POST',
      header: {
        'content-type': 'application/json'
      },
      timeout: 10000,
      data: {
        name,
        wechat_id,
        openid: app.globalData.openid || '',  // 开发阶段可能为空
        gender,
        check_in,
        check_out,
        smoking,
        schedule,
        noise_in,
        noise_out,
        user_agreement,
        group_code
      },
      success: (res) => {
        wx.hideLoading()
        if (res.statusCode === 200 && res.data) {
          // 保存用户信息和当前微信号、群口令到全局
          app.globalData.userInfo = res.data
          app.globalData.userInfo.wechat_id = wechat_id
          app.globalData.userInfo.group_code = group_code
          // 跳转到结果页
          wx.redirectTo({
            url: '/pages/result/result'
          })
        } else {
          wx.showToast({
            title: res.data && res.data.message ? res.data.message : '提交失败，请重试',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        wx.hideLoading()
        console.error('提交失败:', err)
        wx.showToast({
          title: '网络连接失败，请检查网络后重试',
          icon: 'none',
          duration: 2000
        })
      }
    })
  }
})
