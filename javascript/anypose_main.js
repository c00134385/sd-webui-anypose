function initElements() {
    let Elements = {
        anyPoseView1: getGradioElement('#anypose-view1'),
        anyPoseView2: getGradioElement('#anypose-view2'),
        txt2img: getGradioElement("#txt2img_prompt_container"),
        img2img: getGradioElement("#img2img_prompt_container"),
        btnReload: document.querySelectorAll('.anypose-reload'),
    }
    return Elements
}

function getGradioElement(key) {
    return gradioApp().querySelector(key)
}

function initView(){
    let Elements = initElements()
    Elements.txt2img.appendChild(Elements.anyPoseView1)
    Elements.img2img.appendChild(Elements.anyPoseView2)


    Elements.btnReload= document.querySelectorAll('.anypose-reload');
    Elements.btnReload.forEach((item,index) => {
        item.dataset.page=index
        item.addEventListener('click', () => {  
            console.log('reload is clicked.')
            initData()
        })
    })
}

async function initData(){
    divs= document.querySelectorAll('.anypose-tabs')
    divs.forEach(item=>{
        item.remove()
    })

    await new Promise(resolve => setTimeout(resolve, 1500));
    let Elements = initElements()
    let val1 = document.querySelector("#anypose-area1 textarea").value
    let val2 = document.querySelector("#anypose-area2 textarea").value
    let jsonstr = val1||val2
    console.log('jsonstr:', jsonstr)   
    if (jsonstr) {
        initNodes(jsonstr, Elements.btnReload[0])
        initNodes(jsonstr, Elements.btnReload[1])
    }
}

function onTabClick(self){
    let selfdivs=self.parentNode.children
    let contents=self.parentNode.nextSibling.children
    let index=self.dataset.tabitem
  
    for (let i = 0; i < selfdivs.length; i++) {
        if(i==index){
            contents[i].classList.remove('six-hide')
            selfdivs[i].classList.add('selected')
        }
        else{
            contents[i].classList.add('six-hide')
            selfdivs[i].classList.remove('selected')
        }
    }
}

function enumUnits(obj,parent,pageindex) {
    for (var key in obj) {     
        let btn=document.createElement('button')
        setCss(btn,'sm secondary gradio-button svelte-1ipelgc oldsix-btn')
        btn.innerHTML=key
        btn.dataset.sixoldtit=obj[key]
        btn.dataset.pageindex=pageindex
        parent.appendChild(btn)
        btn.addEventListener('click',function(e){    
            // addPrompt(e)
            console.log(e, ' is clicked')
        })
        btn.addEventListener('contextmenu', function (e) {
            e.preventDefault();
            // addNPrompt(e)
            console.log(e, ' is clicked right')
        })
    }
}

function initNodes(jsonstring, btnreloadDom) {
    let jsonObj = JSON.parse(jsonstring)
    let tabs = document.createElement('div')
    let tabnav = document.createElement('div')
    let contentContainer=document.createElement('div')
    let count=0
    Object.keys(jsonObj).forEach(function (key) {      
        let tabbtn=CreateEle('button',tabnav,'svelte-1g805jl',key)
        tabbtn.dataset.tabitem=count
        tabbtn.addEventListener('click',()=>{
            onTabClick(tabbtn)
        })
        let tabitem=CreateEle('div',contentContainer,'tab-item six-hide','')
        tabitem.dataset.tabitem=count
        let content=CreateEle('div',tabitem,'','')
        if(count==0){
            tabbtn.classList.add('selected')
            tabitem.classList.remove('six-hide')
        }
        enumUnits(jsonObj[key],content,btnreloadDom.dataset.page)
        count++
    });
  
    setCss(tabs, 'anypose-tabs gradio-tabs svelte-1g805jl')
    setCss(tabnav, 'anypose-tab-nav scroll-hide svelte-1g805jl')
    setCss(contentContainer, 'tab-container')

    tabs.appendChild(tabnav)
    tabs.appendChild(contentContainer)
    btnreloadDom.parentNode.parentNode.appendChild(tabs)
}


onUiLoaded(async => {
    initView()
    initData()
})


 
  
 
 




  