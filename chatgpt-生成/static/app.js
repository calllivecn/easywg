const configListEl = document.querySelector('.config-list')
const addConfigBtnEl = document.getElementById('add-config-btn')
const deleteConfigBtnEl = document.getElementById('delete-config-btn')

let configs = []
let activeConfig = null

function updateConfigList() {
  configListEl.innerHTML = ''
  for (const config of configs) {
    const configItemEl = document.createElement('div')
    configItemEl.classList.add('config-item')
    configItemEl.textContent = config
    if (config === activeConfig) {
      configItemEl.classList.add('active')
    }
    configItemEl.addEventListener('click', () => {
      setActiveConfig(config)
    })
    configListEl.appendChild(configItemEl)
  }
}

function addConfig() {
  const name = prompt('Enter the name of the new configuration:')
  if (name && !configs.includes(name)) {
    configs.push(name)
    updateConfigList()
  }
}

function deleteConfig() {
  if (activeConfig) {
    const index = configs.indexOf(activeConfig)
    if (index !== -1) {
      configs.splice(index, 1)
      setActiveConfig(null)
      updateConfigList()
    }
  }
}

function setActiveConfig(config) {
  activeConfig = config
  updateConfigList()
}

addConfigBtnEl.addEventListener('click', addConfig)
deleteConfigBtnEl.addEventListener('click', deleteConfig)

// Initialize the UI
configs = ['config1', 'config2'] // Replace with actual configs
activeConfig = configs[0]
updateConfigList()


