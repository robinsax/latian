/**
* Frontend logic for the WebSocket I/O source.
*/
{ // Lexical block so top-level const is safe.
const { Fragment, render, h } = preact;
const { useState, useMemo, useEffect } = preactHooks;

const PORT = '$PORT';
const MESSAGE_TYPES = ['message', 'event', 'exercise'];
const ERROR_HTML = '<div class="output error-message">error</div>';

// Logic.

const classList = set => set.filter(check => check).join(' ');

/**
* Return the unescaped option text if it was a control option and
* null otherwise.
*/
const asControlOption = option => {
    const lastK = option.length - 1;
    if (option[0] == '<' && option[lastK] == '>') {
        return option.substring(1, lastK);
    }

    return null;
};

/**
* Format a rep count or time value into a string.
*/
const formatValue = (value, type, isDifference=false) => {
    const negative = value < 0;
    if (negative) value *= -1;

    let format;
    if (type == 'rep') format = 'x' + value;
    else {
        format = (value % 60) + 's';
        if (value >= 60) {
            format = Math.floor(value / 60) + 'm' + format;
        }
    }

    if (negative) format = '-' + format;
    else if (isDifference) {
        if (value > 0) format = '+' + format;
        else format = '-';
    }

    return format;
};

// TODO: Better communication.
const isLogEvent = output => (
    output.type == 'event' && output.data.prefix == '+'
);

/**
* Manages I/O and provide the current list of outputs to observers
* via callbacks.
*/
class IOManager {
    _socket = null;
    _outputs = [];
    _observers = [];

    constructor() {
        this._handleOutput = this._handleOutput.bind(this);
        this._handleError = this._handleError.bind(this);
    }

    bind() {
        const address = 'ws://localhost:' + PORT + '/ws';
        this._socket = new WebSocket(address);

        this._socket.addEventListener('message', this._handleOutput);
        this._socket.addEventListener('error', this._handleError);
        this._socket.addEventListener('close', this._handleError);
    }

    observe(callbackFn) {
        this._observers.push(callbackFn);
        callbackFn(this._outputs);
    }

    send(input) {
        this._socket.send(JSON.stringify({ input }));
    }

    _handleError() {
        document.body.className = 'connection-error';
        document.body.innerHTML = ERROR_HTML;
    }

    _handleOutput(event) {
        const output = JSON.parse(event.data);

        this._outputs = this._processOutput(output);
        for (const callbackFn of this._observers) {
            callbackFn(this._outputs);
        }
    }
    
    _processOutput(output) {
        const lastK = this._outputs.length - 1;

        // TODO: Better communication.
        const sessionStart = (
            output.data?.options?.includes('random') ||
            output.data == 'next exercise'
        );
        if (sessionStart) document.body.className = 'in-session';
    
        const sessionEnd = (
            output.data?.message == 'what do you want to do'
        );
        if (sessionEnd) document.body.className = '';
    
        switch (output.type) {
            case 'input_invalid':
                return [
                    ...this._outputs.slice(0, lastK),
                    { 
                        ...this._outputs[lastK],
                        data: {
                            ...this._outputs[lastK].data,
                            invalid: true
                        }
                    }
                ];
            case 'input_ok':
                return [...this._outputs.slice(0, lastK)];
            case 'unwrite_timer':
                return this._outputs.filter(check => (
                    check.type != 'timer'
                ));
            case 'unwrite_messages':
                let removed = 0;
                return this._outputs.reverse().filter(check => {
                    if (removed >= output.data) return true;
                    if (!MESSAGE_TYPES.includes(check.type)) {
                        return true;
                    }
   
                    removed++;
                    return false;
                }).reverse();
            default:
                return [...this._outputs, output]
        }
    }
}

// Components.

const Message = ({ data: message }) => (
    h('div', {
        class: classList([
            'message',
            message.startsWith('-') &&
            message.endsWith('-') &&
            'heading'
        ])
    }, (
        message.replace(/\s-+|-+\s/g, '')
    ))
);

const Event = ({ data: { type, exercise, value, prefix } }) => {
    // TODO: Better communication.
    const isDifference = prefix == '+/-';

    const formatted = useMemo(() => (
        formatValue(value, type, isDifference)
    ), [value, type]);

    return (
        h('div', {
            class: classList([
                'message',
                exercise.startsWith('milestone') && 'milestone',
                isDifference && value > 0 && 'difference-plus',
                isDifference && value < 0 && 'difference-minus'
            ])
        }, [
            prefix &&
            h('div', { class: 'secondary width-a' }, prefix),
            h('div', { class: 'width-b' }, exercise),
            h('div', { class: 'secondary width-a' }, type),
            h('div', { class: 'width-b' }, formatted)
        ])
    );
};

const Input = ({
    io, data: { options, signal_only, message, invalid }
}) => (
    h('div', {
        class: classList([
            'input',
            invalid && 'invalid',
            signal_only && 'signal-only'
        ])
    }, [
        h('div', { class: 'input-label' }, message),
        signal_only ?
            h('button', {
                class: 'input-field',
                onClick: () => io.send('signal')
            }, '✔️')
        : options ?
            h('div', {
                class: 'options input-field'
            }, (
                options.map(option => (asControl => (
                    h('button', {
                        key: option,
                        class: classList([
                            asControl && 'control'
                        ]),
                        onClick: () => io.send(option)
                    }, asControl || option)
                ))(asControlOption(option)))
            ))
        :
            h('input', {
                class: 'input-field',
                ref: el => el && el.focus(),
                onKeyUp: event => (
                    event.which == 13 && io.send(event.target.value)
                )
            })
    ])
);

const Exercise = ({ data: { type, name, prefix }}) => (
    h('div', { class: 'message' }, [
        prefix &&
        h('div', { class: 'secondary width-a' }, prefix),
        h('div', { class: 'width-b' }, name),
        h('div', { class: 'secondary width-a' }, type)
    ])
);

const Timer = ({ data: delay }) => {
    const [time, setTime] = useState(-delay);

    useEffect(() => {
        const start = Date.now() + (delay * 1000);
        const interval = setInterval(() => {
            const now = Date.now();

            setTime(Math.floor((now - start) / 1000));
        }, 100);

        return () => clearInterval(interval);
    }, []);

    return h('dev', { class: 'timer' }, (
        formatValue(time, 'timed')
    ));
};

const DebugOutput = ({ type, data }) => (
    h('div', { class: 'unknown' }, (
        JSON.stringify({ type, data })
    ))
);

const Output = ({ io, type, data }) => (
    h(
        type == 'message' ? Message :
        type == 'input' ? Input :
        type == 'timer' ? Timer :
        type == 'event' ? Event :
        type == 'exercise' ? Exercise :
        DebugOutput,
        { io, type, data }
    )
);

const Root = ({ io }) => {
    const [outputs, setOutputs] = useState([]);

    useEffect(() => io.observe(setOutputs), []);

    const [logEvents, otherOutputs] = useMemo(() => (
        [
            outputs.filter(isLogEvent).reverse(),
            outputs.filter(output => !isLogEvent(output))
        ]
    ), [outputs]);

    return h(Fragment, null, [
        h('div', { class: 'log' }, (
            logEvents.map((event, k) => (
                h(Output, { key: k, ...event })
            ))
        )),
        h('div', { class: 'output' }, (
            otherOutputs.map((output, k) => (
                h(Output, { key: k, io, ...output })
            ))
        ))
    ]);
};

// Main.

const main = () => {
    const io = new IOManager();

    io.bind();

    render(h(Root, { io }), document.querySelector('#root'));
};
main();

}