package main

import (
    "encoding/json"
    "log"
    "net/http"
    "os"
    "strings"
    "time"

    "github.com/miekg/dns"
)

type Rules struct {
    BlockDomains []string `json:"block_domains"`
}

var rules Rules

func loadRules() {
    f, err := os.Open("rules.json")
    if err != nil {
        return
    }
    defer f.Close()
    json.NewDecoder(f).Decode(&rules)
}

func isBlocked(qname string) bool {
    host := strings.TrimSuffix(qname, ".")
    for _, d := range rules.BlockDomains {
        if host == d || strings.HasSuffix(host, "."+d) {
            return true
        }
    }
    return false
}

func handleDNS(w dns.ResponseWriter, r *dns.Msg) {
    m := new(dns.Msg)
    m.SetReply(r)
    if len(r.Question) == 0 {
        w.WriteMsg(m)
        return
    }
    q := r.Question[0]
    if q.Qtype == dns.TypeA || q.Qtype == dns.TypeAAAA {
        if isBlocked(q.Name) {
            m.Rcode = dns.RcodeNameError
            w.WriteMsg(m)
            return
        }
        c := new(dns.Client)
        resp, _, err := c.Exchange(r, "1.1.1.1:53")
        if err != nil {
            m.Rcode = dns.RcodeServerFailure
            w.WriteMsg(m)
            return
        }
        w.WriteMsg(resp)
        return
    }
    c := new(dns.Client)
    resp, _, err := c.Exchange(r, "1.1.1.1:53")
    if err != nil {
        m.Rcode = dns.RcodeServerFailure
        w.WriteMsg(m)
        return
    }
    w.WriteMsg(resp)
}

func syncRulesFromAPI() {
    ticker := time.NewTicker(10 * time.Second)
    for range ticker.C {
        resp, err := http.Get("http://localhost:8080/rules")
        if err != nil {
            continue
        }
        defer resp.Body.Close()
        var apiRules []struct{ Domain string }
        json.NewDecoder(resp.Body).Decode(&apiRules)
        var newRules Rules
        for _, r := range apiRules {
            newRules.BlockDomains = append(newRules.BlockDomains, r.Domain)
        }
        rules = newRules
    }
}

func main() {
    loadRules()
    go syncRulesFromAPI()
    dns.HandleFunc(".", handleDNS)
    udpServer := &dns.Server{Addr: ":5353", Net: "udp"}
    tcpServer := &dns.Server{Addr: ":5353", Net: "tcp"}
    go udpServer.ListenAndServe()
    tcpServer.ListenAndServe()
}
