const button = document.querySelector('.button-circle')
const outerCircle = document.querySelector('.outer-circle')
const price = document.querySelector('.price')

let lastangle = 0
const setAngle = unNormalizedAngle => {
    const angle = unNormalizedAngle < 0 ? unNormalizedAngle + 360 : unNormalizedAngle
    const anglePercent = Math.round(angle / 360 * 100)
    if (Math.abs(angle - lastangle) > 180){
    return
    }

    button.style.transform = `rotateZ(${angle}deg)`
    outerCircle.style.background = `conic-gradient(green ${anglePercent}%, black 0)`
    price.innerText = `${anglePercent}%`
    lastangle = angle
}

const handler = (event) =>{
    const rect = outerCircle.getBoundingClientRect()
    const x = event.pageX - (rect.left + rect.width/2)
    const y = -(event.pageY - (rect.top + rect.height/2))
    const angle = Math.atan2(y,x) * 180 / Math.PI
    setAngle(-(angle-90))
}

button.addEventListener('mousedown', () => {
    window.addEventListener('mousemove', handler)
})

window.addEventListener('mouseup', () => {
    window.removeEventListener('mousemove', handler)
})