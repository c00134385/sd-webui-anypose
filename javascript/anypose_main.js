// function loadNodes() {
//     let Elements = {
//         prompt: getEle('#anypose-prompt1'),
//         prompt2: getEle('#anypose-prompt2'),
//         txt2img: getEle("#txt2img_prompt_container"),
//         img2img: getEle("#img2img_prompt_container"),
//     }
//     return Elements
// }

function getEle_(key) {
    return gradioApp().querySelector(key)
}

function moveUi(){
    let Elements = {
        prompt: getEle_('#anypose-prompt1'),
        prompt2: getEle_('#anypose-prompt2'),
        txt2img: getEle_("#txt2img_prompt_container"),
        img2img: getEle_("#img2img_prompt_container"),
    }
    console.log('AnyPose move is called.', Elements)
    console.log('AnyPose move is called.', Elements.txt2img)
    console.log('AnyPose move is called.', Elements.img2img)
    Elements.txt2img.appendChild(Elements.prompt)
    Elements.img2img.appendChild(Elements.prompt2)
}

onUiLoaded(async => {
    console.log('AnyPose onUiLoaded is called.')
    moveUi()
})


 
  
 
 




  