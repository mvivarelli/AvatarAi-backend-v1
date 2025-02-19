var pc = null;

function negotiate() {
    pc.addTransceiver('video', { direction: 'recvonly' });
    pc.addTransceiver('audio', { direction: 'recvonly' });
    return pc.createOffer().then(function (offer) {
        return pc.setLocalDescription(offer);
    }).then(function () {
        // wait for ICE gathering to complete
        return new Promise(function (resolve) {
            if (pc.iceGatheringState === 'complete') {
                resolve();
            } else {
                function checkState() {
                    if (pc.iceGatheringState === 'complete') {
                        pc.removeEventListener('icegatheringstatechange', checkState);
                        resolve();
                    }
                }
                pc.addEventListener('icegatheringstatechange', checkState);
            }
        });
    }).then(function () {
        var offer = pc.localDescription;
        return fetch('/offer', {
            body: JSON.stringify({
                sdp: offer.sdp,
                type: offer.type,
                video_transform: "No transform"
            }),
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'POST'
        });
    }).then(function (response) {
        return response.json();
    }).then(function (answer) {
        return pc.setRemoteDescription(answer);
    }).catch(function (e) {
        alert(e);
    });
}

function start() {
    var config = {
        sdpSemantics: 'unified-plan'
    };

    //config.iceServers = [{ urls: ['stun:stun.relay.metered.ca:80'] }];
    config.iceServers = [{ urls: ['stun:stun.1und1.de:3478'] }];
    //config.iceServers = [{ urls: ['stun:stun.1und1.de:3478', 'stun:stun.relay.metered.ca:80'] }];

    pc = new RTCPeerConnection(config);

    // connect audio / video
    pc.addEventListener('track', function (evt) {
        if (evt.track.kind == 'video') {
            document.getElementById('video').srcObject = evt.streams[0];
            document.getElementById('video').addEventListener('ended', function () {
                console.log('Video stream ended');
            });
        } else {
            document.getElementById('audio').srcObject = evt.streams[0];
        }
    });

    negotiate();
}

function stop() {
    // close peer connection
    setTimeout(function () {
        pc.close();
    }, 500);
}

// Auto start when the page loads
window.addEventListener('load', function () {
    start();
});