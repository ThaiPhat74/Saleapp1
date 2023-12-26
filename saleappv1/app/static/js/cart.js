function addToCart(id, name, price) {
    fetch("/api/cart", {
        method: "post",
        body: JSON.stringify({
            "id": id,
            "name": name,
            "price": price
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(function(res) {
        return res.json();
    }).then(function(data) {
        let carts = document.getElementsByClassName("cart-counter");
        for (let d of carts)
            d.innerText = data.total_quantity;
    });
}

function updateCart(id, obj) {
    obj.disabled = true;
    fetch(`/api/cart/${id}`, {
        method: "put",
        body: JSON.stringify({
            "quantity": obj.value
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(function(res) {
        return res.json();
    }).then(function(data) {
        obj.disabled = false;
        let carts = document.getElementsByClassName("cart-counter");
        for (let d of carts)
            d.innerText = data.total_quantity;

        let amounts = document.getElementsByClassName("cart-amount");
        for (let d of amounts)
            d.innerText = data.total_amount.toLocaleString("en");
    });
}

function deleteCart(id, obj) {
    if (confirm("Bạn chắc chắn xóa?") === true) {
        obj.disabled = true;
        fetch(`/api/cart/${id}`, {
            method: "delete"
        }).then(function(res) {
            return res.json();
        }).then(function(data) {
            obj.disabled = false;
            let carts = document.getElementsByClassName("cart-counter");
            for (let d of carts)
                d.innerText = data.total_quantity;

            let amounts = document.getElementsByClassName("cart-amount");
            for (let d of amounts)
                d.innerText = data.total_amount.toLocaleString("en");


            let t = document.getElementById(`product${id}`);
            t.style.display = "none";
        });
    }
}

function pay() {
    if (confirm("Bạn chắc chắn thanh toán!") === true) {
        fetch("/api/pay", {
            method: "post"
        }).then(res => res.json()).then(data => {
            if (data.status === 200)
                location.reload();
            else
                alert(data.err_msg)
        })
    }
}

function addComment(productId){
    let content = document.getElementById('commentId')
    if(content !== null){
        fetch('/api/comments', {
            method:'post',
            body:JSON.stringify({
                'product_id':productId,
                'content':content.value
            }),
            headers:{
                'Content-Type':'application/json'
            }
        }).then(res => res.json()).then(data =>{
            if(data.status == 201){
                let c = data.comment

                let area = document.getElementById('commentArea')

                area.innerHTML = `
                <div class=" row">
                    <div class="col-md-1 col-xs-4">
                        <img src="${c.user.avatar}" class="img-fluid rounded-circle" alt="demo" />
                    </div>
                    <div class="col-md-11 col-xs-8">
                        <p>${c.content}</p>
                        <p><em>${moment(c.created_date).locale('vi').fromNow()}</em></p>
                    </div>
                ` + area.innerHTML
            } else if(data.status == 404)
                alert(data.err_msg)
        })
    }
}
