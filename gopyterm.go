package gopyterm

import (
    "bufio"
    "fmt"
    "io"
    "os"
    "os/exec"
    "path/filepath"
    "runtime"
)

const RENDERER = "pygame_renderer.py"

var stdout_chan = make(chan string)

var stdin_pipe io.WriteCloser
var stdout_pipe io.ReadCloser
var stderr_pipe io.ReadCloser

func pipe_relay(p io.ReadCloser, ch chan string, f io.ReadWriteCloser) {

    // Relay a pipe to both a channel and a file (though either can be nil)

    scanner := bufio.NewScanner(p)

    for scanner.Scan() {

        s := scanner.Text()

        if ch != nil {
            ch <- s
        }

        if f != nil {
            fmt.Fprintf(f, "%s\n", s)
        }
    }
}

func Char(c byte, x int32, y int32, colour string) error {

    if c > 127 {
        return fmt.Errorf("send_line(): character was > 127")
    }

    _, err := fmt.Fprintf(stdin_pipe, "%d %d %d red\n", c, x, y)
    if err != nil {
        return fmt.Errorf("Char(): %v", err)
    }

    return nil
}

func Draw() error {

    _, err := fmt.Fprintf(stdin_pipe, "DRAW\n")
    if err != nil {
        return fmt.Errorf("Draw(): %v", err)
    }

    <- stdout_chan

    return nil
}

func Start(width int, height int) error {

    w := fmt.Sprintf("%d", width)
    h := fmt.Sprintf("%d", height)

    _, filename, _, _ := runtime.Caller(0)
    dir := filepath.Dir(filename)
    renderer := filepath.Join(dir, RENDERER)
    charfile := filepath.Join(dir, "chars8x12.png")

    exec_command := exec.Command(
        "python", renderer, "--width", w, "--height", h, "--charwidth", "8", "--charheight", "12", "--charfile", charfile)

    stdin_pipe, _ = exec_command.StdinPipe()
    stdout_pipe, _ = exec_command.StdoutPipe()
    stderr_pipe, _ = exec_command.StderrPipe()

    go pipe_relay(stdout_pipe, stdout_chan, nil)
    go pipe_relay(stderr_pipe, nil, os.Stderr)

    err := exec_command.Start()
    if err != nil {
        return fmt.Errorf("Start(): %v", err)
    }

    return nil
}
