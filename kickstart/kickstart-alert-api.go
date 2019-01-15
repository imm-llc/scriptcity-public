package main

import (
	"fmt"
	"net/http"

	slack "github.com/ashwanthkumar/slack-go-webhook"
)

func slackPost(response http.ResponseWriter, request *http.Request) {
	webhookURL := ""
	channelID := "#ks-notifications"

	payload := slack.Payload{
		Text:     "Kickstart install complete!",
		Username: "Kickstart Bot",
		Channel:  channelID,
		IconUrl:  "https://upload.wikimedia.org/wikipedia/commons/a/af/Tux.png",
	}
	err := slack.Send(webhookURL, "", payload)
	if err != nil {
		fmt.Println(err)
	}

}
func main() {
	http.HandleFunc("/", slackPost)
	err := http.ListenAndServe(":3131", nil)
	if err != nil {
		panic(err)
	}
}
