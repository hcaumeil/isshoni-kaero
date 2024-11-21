import { Component, inject, OnInit } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { environment } from "../../environments/environment";
import { Router } from "@angular/router";

type Contact = {
  id: string;
  name: string;
};

type Message = {
  id: string;
  content: string;
  sender: string;
  sent_at: string;
};

@Component({
  selector: "app-home",
  standalone: true,
  imports: [FormsModule],
  templateUrl: "./home.component.html",
  styleUrl: "./home.component.css",
})
export class HomeComponent implements OnInit {
  user = localStorage.getItem("user");
  router = inject(Router);
  channel: string | null = null;
  contacts: Contact[] = [];
  messages: Message[] = [];
  content = "";

  ngOnInit(): void {
    fetch(environment.api_url + "/channels/", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + localStorage.getItem("token"),
      },
    }).then((res) => res.json().then((val) => this.contacts = val));
  }

  select(e: any) {
    this.channel = e.target.value;
    fetch(environment.api_url + "/messages/" + this.channel, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + localStorage.getItem("token"),
      },
    }).then((res) => res.json().then((val) => this.messages = val));
  }

  send() {
    fetch(environment.api_url + "/messages/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + localStorage.getItem("token"),
      },
      body: JSON.stringify({
        channel: this.channel,
        content: this.content,
      }),
    }).then((res) => {
      this.select({ target: { value: this.channel } });
    });
  }

  channelplus() {
    this.router.navigate(["/add"]);
  }

  disconnect() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    this.router.navigate(["/login"]);
  }
}
