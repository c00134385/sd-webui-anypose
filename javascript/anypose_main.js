function initElements() {
    let Elements = {
        txt2img_anypose: getGradioElement('#txt2img_anypose'),
        img2img_anypose: getGradioElement('#img2img_anypose'),
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

function initView() {
    let Elements = initElements()
    Elements.txt2img.appendChild(Elements.txt2img_anypose)
    Elements.img2img.appendChild(Elements.img2img_anypose)

    // Elements.btnReload= document.querySelectorAll('.anypose-reload');
    // Elements.btnReload.forEach((item,index) => {
    //     item.dataset.page=index
    //     item.addEventListener('click', () => {  
    //         console.log('reload is clicked.')
    //         initData()
    //     })
    // })
}

async function initData() {
    divs = document.querySelectorAll('.anypose-tabs')
    divs.forEach(item => {
        item.remove()
    })

    await new Promise(resolve => setTimeout(resolve, 1500));
    let Elements = initElements()
    let val1 = document.querySelector("#anypose-area1 textarea").value
    let val2 = document.querySelector("#anypose-area2 textarea").value
    let jsonstr = val1 || val2
    console.log('jsonstr**:', jsonstr)
    if (jsonstr) {
        initNodes(jsonstr, Elements.btnReload[0])
        initNodes(jsonstr, Elements.btnReload[1])
    }
}

function onTabClick(self) {
    let selfdivs = self.parentNode.children
    let contents = self.parentNode.nextSibling.children
    let index = self.dataset.tabitem

    for (let i = 0; i < selfdivs.length; i++) {
        if (i == index) {
            contents[i].classList.remove('six-hide')
            selfdivs[i].classList.add('selected')
        }
        else {
            contents[i].classList.add('six-hide')
            selfdivs[i].classList.remove('selected')
        }
    }
}

function enumUnits(obj, parent, pageindex) {
    for (var key in obj) {
        let btn = document.createElement('button')
        setCss(btn, 'sm secondary gradio-button svelte-1ipelgc oldsix-btn')
        btn.innerHTML = key
        btn.dataset.sixoldtit = obj[key]
        btn.dataset.pageindex = pageindex
        parent.appendChild(btn)
        btn.addEventListener('click', function (e) {
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
    let contentContainer = document.createElement('div')
    let count = 0
    Object.keys(jsonObj).forEach(function (key) {
        let tabbtn = CreateEle('button', tabnav, 'svelte-1g805jl', key)
        tabbtn.dataset.tabitem = count
        tabbtn.addEventListener('click', () => {
            onTabClick(tabbtn)
        })
        let tabitem = CreateEle('div', contentContainer, 'tab-item six-hide', '')
        tabitem.dataset.tabitem = count
        let content = CreateEle('div', tabitem, '', '')
        if (count == 0) {
            tabbtn.classList.add('selected')
            tabitem.classList.remove('six-hide')
        }
        enumUnits(jsonObj[key], content, btnreloadDom.dataset.page)
        count++
    });

    setCss(tabs, 'anypose-tabs gradio-tabs svelte-1g805jl')
    setCss(tabnav, 'anypose-tab-nav scroll-hide svelte-1g805jl')
    setCss(contentContainer, 'tab-container')

    tabs.appendChild(tabnav)
    tabs.appendChild(contentContainer)
    btnreloadDom.parentNode.parentNode.appendChild(tabs)
}


function anypose_saveImage() {
    let txt2img_anypose_image_container = gradioApp().querySelector("#txt2img_anypose_image")
    let img2img_anypose_image_container = gradioApp().querySelector("#img2img_anypose_image")
    var items = txt2img_anypose_image_container.querySelectorAll('img')
    if (items.length > 0) {
        let img = items[0]
        console.log(img)
        console.log(img.src)
        save2PNG(img.src)
    }
}

function anypose_sendImage() {
    console.log("anypose_sendImage is called.")
    let txt2img_anypose_image_container = gradioApp().querySelector("#txt2img_anypose_image")
    let img2img_anypose_image_container = gradioApp().querySelector("#img2img_anypose_image")
    var items = txt2img_anypose_image_container.querySelectorAll('img')
    if (items.length > 0) {
        let img = items[0]
        console.log(img)
        console.log(img.src)
        send2CN(img.src)
    }
}

function send2CN(imgSrc) {
    var link = document.createElement('a');
    var canvas = document.createElement('canvas');
    var image = new Image();
    image.src = imgSrc;

    image.onload = function () {
        console.log("anypose_sendImage is called.-- 1")
        canvas.width = image.width;
        canvas.height = image.height;
        var context = canvas.getContext('2d');
        context.drawImage(image, 0, 0);

        canvas.toBlob(async function (blob) {
            console.log("anypose_sendImage is called.-- 2")
            const file = new File(([blob]), "pose.png");
            const dt = new DataTransfer();
            dt.items.add(file);
            const list = dt.files;
            const divControlNet = depth_gradioApp().querySelector("#txt2img_controlnet");
            console.log("anypose_sendImage is called.-- 3", divControlNet)
            if (divControlNet) {
                // open the ControlNet accordion if it's not already open
                // but give up if it takes longer than 5 secs
                labelControlNet = divControlNet.querySelector("div.label-wrap");
                console.log("anypose_sendImage is called.-- 4")
                if (!labelControlNet.classList.contains("open")) {
                    console.log("anypose_sendImage is called.-- 5")
                    labelControlNet.click();
                    let waitUntilHasClassOpenCount = 0;
                    const waitUntilHasClassOpen = async () => {
                        waitUntilHasClassOpenCount++;
                        if (waitUntilHasClassOpenCount > 50) {
                            return false;
                        } else if (labelControlNet.classList.contains("open")) {
                            return true;
                        } else {
                            setTimeout(() => waitUntilHasClassOpen(), 100)
                        }
                    };
                    await waitUntilHasClassOpen();
                }
                console.log("anypose_sendImage is called.-- 6")

                // const input = divControlNet.querySelector("input[type='file']");
                // const button = divControlNet.querySelector("button[aria-label='Clear']")
                // button && button.click();
                // input.value = "";
                // input.files = list;
                // const event = new Event('change', { 'bubbles': true, "composed": true });
                // input.dispatchEvent(event);
                
                const div_generated_image_group = divControlNet.querySelector("#txt2img_controlnet_ControlNet-0_generated_image");
                const input_generated_image_group = div_generated_image_group.querySelector("input[type='file']")
                console.log('input_generated_image_group:', input_generated_image_group)
                input_generated_image_group.value = "";
                input_generated_image_group.files = list;
                const event1 = new Event('change', { 'bubbles': true, "composed": true });
                input_generated_image_group.dispatchEvent(event1);

                // enable controlnet
                const controlnet_enable_checkbox = divControlNet.querySelector("#txt2img_controlnet_ControlNet-0_controlnet_enable_checkbox input[type='checkbox']")
                if(controlnet_enable_checkbox && !controlnet_enable_checkbox.checked) {
                    controlnet_enable_checkbox.click()
                }

                // enable preview
                const preview_checkbox = divControlNet.querySelector("#txt2img_controlnet_ControlNet-0_controlnet_preprocessor_preview_checkbox input[type='checkbox']")
                console.log('preview_checkbox:', preview_checkbox)
                if(preview_checkbox && !preview_checkbox.checked) {
                    preview_checkbox.click()
                }
                
                // Ä£ÄâÓÃ»§µã»÷ÊÂ¼þ
                // enable preview-as-input
                const preview_as_input_checkbox = divControlNet.querySelector(".cnet-preview-as-input input[type='checkbox']")
                console.log("preview_as_input_checkbox:", preview_as_input_checkbox)
                if(preview_as_input_checkbox && !preview_as_input_checkbox.checked) {
                    preview_as_input_checkbox.click()
                }

                // control types: select openpose
                const controlnet_control_types = divControlNet.querySelectorAll("#txt2img_controlnet_ControlNet-0_controlnet_type_filter_radio input[type='radio']")
                console.log('controlnet_control_types:', controlnet_control_types)
                controlnet_control_types.forEach(e => {
                    console.log('controlnet_control_types e:', e, e.value)
                    if(e.value === 'OpenPose' && !e.checked) {
                        e.click()
                    }
                });
            }
        }, 'image/png');
    };

    document.body.appendChild(link);
}

function save2PNG(imgSrc) {
    var link = document.createElement('a');
    var canvas = document.createElement('canvas');
    var image = new Image();
    image.src = imgSrc;

    image.onload = function () {
        canvas.width = image.width;
        canvas.height = image.height;
        var context = canvas.getContext('2d');
        context.drawImage(image, 0, 0);

        canvas.toBlob(function (blob) {
            // å°†Blobå¯¹è±¡ä¿å­˜ä¸ºæ–‡ä»?
            link.href = URL.createObjectURL(blob);
            link.download = 'image.png';
            link.click();
            // é‡Šæ”¾èµ„æº
            URL.revokeObjectURL(link.href);
        }, 'image/png');
    };

    document.body.appendChild(link);
}

onUiLoaded(async => {
    initView()
    // initData()
})