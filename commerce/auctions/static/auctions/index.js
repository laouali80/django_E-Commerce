
document.addEventListener('DOMContentLoaded', function() {
    
    const auctions = document.querySelectorAll("[id~='auction']");

    auctions.forEach(auction => {

        const auctionEndDate = auction.querySelector("#end-date")
        const countdownBox = auction.querySelector("#countdown-box")

        // console.log(auctionEndDate.textContent + " " + countdownBox.textContent)

        const eventDate = Date.parse(auctionEndDate.textContent)

        // console.log(eventDate)


        const myCountdown = setInterval(()=>{
            const now = new Date().getTime()

            const diff = eventDate - now

            const d = Math.floor(eventDate / (1000 * 60 * 60 * 24) - (now / (1000 * 60 * 60 * 24) ) )
            const h = Math.floor((eventDate / (1000 * 60 * 60) - (now / (1000 * 60 * 60) )) % 24)
            const m = Math.floor((eventDate / (1000 * 60) - (now / (1000 * 60) )) % 60 )
            const s = Math.floor((eventDate / (1000) - (now / (1000) )) % 60 )

            // console.log(d + " " + h + " " + m + "" + s)

            // console.log(now)

            if (diff>0) {
                // console.log("repeat")
                if (d>0) {
                    countdownBox.innerHTML = d + " days, " + h + " hour, " + m + " minutes, " + s + " seconds"
                }else if (h>0) {
                    countdownBox.innerHTML = h + " hour, " + m + " minutes, " + s + " seconds"
                }else if (m>0) {
                    if (3 < m <= 5){
                        countdownBox.setAttribute("class", "text-warning") 
                        countdownBox.innerHTML = m + " minutes, " + s + " seconds"   
                    }else if (m <= 3) {
                        countdownBox.setAttribute("class", "text-danger")
                        countdownBox.innerHTML = m + " minutes, " + s + " seconds"
                    }else {
                        countdownBox.innerHTML = m + " minutes, " + s + " seconds"
                    }
                    
                }else {
                    countdownBox.innerHTML = s + " seconds"
                }
                
            }else{
                console.log(" no repeat")
                // to clear or stop a set time interval
                clearInterval(myCountdown)
                countdownBox.innerHTML = "Auction Ended"
            }
        }, 1000)
    })

})

