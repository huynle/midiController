// var easymidi = require('easymidi');

// // this statement might turn  on the mixer?
// var inputs = easymidi.getInputs();
// console.log(inputs);

// // var scene = parseInt(process.argv[2]) || 1;

// var qchan = 0;
// var qu = new easymidi.Output('QU-32:QU-32 MIDI 1 20:0');
// console.log("switch to scene: "+scene);
// qu.send('cc', { controller: 0x00, value: 0x00, channel: qchan }); // MSB
// qu.send('cc', { controller: 0x20, value: 0x00, channel: qchan }); // LSB
// qu.send('program', {number: scene-1, channel: qchan});


var easymidi = require('easymidi');
var inputs = easymidi.getInputs();
console.log(inputs);

var scene = parseInt(process.argv[2]) || 1;

var qchan = 0;
var qu = new easymidi.Output('QU-32:QU-32 MIDI 1 20:0');
console.log("switch to scene: "+scene);
qu.send('cc', { controller: 0x00, value: 0x00, channel: qchan }); // MSB
qu.send('cc', { controller: 0x20, value: 0x00, channel: qchan }); // LSB
qu.send('program', {number: scene-1, channel: qchan});
