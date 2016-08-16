package main

import (
    "math/rand"

    term "github.com/fohristiwhirl/gopyterm"
)

func main() {

    term.Start(80, 40)

    for {

        for i := 0 ; i < 128 ; i++ {

            c := byte(rand.Int31n(128))
            x := rand.Int31n(80)
            y := rand.Int31n(40)

            term.Char(c, x, y, "red")
        }

        term.Draw()
    }
}
