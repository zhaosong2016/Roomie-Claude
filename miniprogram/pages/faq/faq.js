Page({
  data: {
    faqList: [
      {
        id: 1,
        question: '你能用我做什么？',
        answer: '帮你在参加会议、活动时，找到合适的室友一起拼房，省钱又能休息好。',
        expanded: false
      },
      {
        id: 2,
        question: '适合谁用？',
        answer: '参加同一活动、想拼房省钱、又在意睡眠质量的人。\n\n欢迎活动组织方使用，帮参会者省钱，轻松提升满意度。',
        expanded: false
      },
      {
        id: 3,
        question: '怎么获得活动口令？',
        answer: '三种角色，都能用：\n\n【官方组织者】（大型活动主办方）\n首页点"创建活动"，系统自动生成口令。分享给所有参会者，覆盖人数越多，匹配成功率越高。\n\n【民间组织者】（自发组局的参会者）\n也是首页点"创建活动"，系统自动生成口令。可以备注自己组织的信息，以与其他组织相区别，方便组员区分。比如你和几个朋友一起参会，想找更多人拼房，自己创建一个口令，在群里分享就行。注意保护群口令，尽量让参与匹配的都是熟人或半熟人，这样更安心。\n\n【普通参会者】\n问组织者要口令，或在活动群里找。拿到口令就能用。但请你尽量在熟悉的群里匹配，并注意个人安全。',
        expanded: false
      },
      {
        id: 4,
        question: '怎么匹配的？',
        answer: '只匹配同性别！我们优先按入住时间和睡眠习惯匹配，帮助你找到习惯相近的室友，让你尽量睡好觉。',
        expanded: false
      },
      {
        id: 5,
        question: '为什么要我确认匹配？',
        answer: '给你 60 秒考虑时间，不想匹配可以重新选择。你的选择权很重要。',
        expanded: false
      },
      {
        id: 6,
        question: '能帮我找到志同道合的朋友吗？',
        answer: '先保证你能睡个好觉。觉睡好了，你们自然就成朋友了。',
        expanded: false
      },
      {
        id: 7,
        question: '忘了匹配的室友是谁怎么办？',
        answer: '重新填一次，系统会提示你之前匹配过谁。',
        expanded: false
      },
      {
        id: 8,
        question: '我的信息安全吗？',
        answer: '只有匹配成功后，对方才能看到你的微信号。其他信息不会泄露。',
        expanded: false
      }
    ]
  },

  onLoad() {
    // 页面加载
  },

  // 切换问题展开/收起
  toggleQuestion(e) {
    const id = e.currentTarget.dataset.id
    const faqList = this.data.faqList.map(item => {
      if (item.id === id) {
        return { ...item, expanded: !item.expanded }
      }
      return item
    })
    this.setData({ faqList })
  }
})
