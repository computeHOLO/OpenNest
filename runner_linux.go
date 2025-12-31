package main

import (
    "bufio"
    "fmt"
    "os"
    "os/exec"
    "strings"
)

func checkDep(name string) bool {
    _, err := exec.LookPath(name)
    return err == nil
}

func askInstall(dep string, installCmd []string) {
    reader := bufio.NewReader(os.Stdin)
    fmt.Printf("%s not found. Install it now? (y/n): ", dep)
    answer, _ := reader.ReadString('\n')
    answer = strings.TrimSpace(strings.ToLower(answer))
    if answer == "y" {
        cmd := exec.Command(installCmd[0], installCmd[1:]...)
        cmd.Stdout = os.Stdout
        cmd.Stderr = os.Stderr
        if err := cmd.Run(); err != nil {
            fmt.Printf("failed to install %s: %v\n", dep, err)
            os.Exit(1)
        }
    } else {
        fmt.Printf("%s is required. Exiting.\n", dep)
        os.Exit(1)
    }
}

func runBackground(name string, args ...string) *exec.Cmd {
    cmd := exec.Command(name, args...)
    cmd.Stdout = os.Stdout
    cmd.Stderr = os.Stderr
    if err := cmd.Start(); err != nil {
        fmt.Printf("error starting %s: %v\n", name, err)
        os.Exit(1)
    }
    return cmd
}

func main() {
    fmt.Println("🪺 OpenNest Linux Runner")

    if !checkDep("go") {
        askInstall("go", []string{"sudo", "apt", "install", "-y", "golang"})
    }
    if !checkDep("python3") {
        askInstall("python3", []string{"sudo", "apt", "install", "-y", "python3"})
    }
    if !checkDep("pip3") {
        askInstall("pip3", []string{"sudo", "apt", "install", "-y", "python3-pip"})
    }
    if !checkDep("npm") {
        askInstall("npm", []string{"sudo", "apt", "install", "-y", "npm"})
    }
    if !checkDep("uvicorn") {
        askInstall("uvicorn", []string{"pip3", "install", "uvicorn[standard]"})
    }

    fmt.Println("Starting DNS service...")
    dns := runBackground("./opennest-dns")

    fmt.Println("Starting API service...")
    api := runBackground("uvicorn", "app:app", "--reload", "--port", "8080")

    fmt.Println("Starting dashboard...")
    web := runBackground("npm", "run", "dev", "--prefix", "web")

    fmt.Println("All services launched. Press Ctrl+C to stop.")

    dns.Wait()
    api.Wait()
    web.Wait()
}
