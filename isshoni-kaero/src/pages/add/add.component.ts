import { Component, inject } from "@angular/core";
import { Router } from "@angular/router";
import { environment } from "../../environments/environment";
import { FormsModule } from "@angular/forms";

@Component({
  selector: "app-add",
  standalone: true,
  imports: [FormsModule],
  templateUrl: "./add.component.html",
  styleUrl: "./add.component.css",
})
export class AddComponent {
  router = inject(Router);
  txtusername: string = "";
  name: string = "";

  add() {
    fetch(environment.api_url + "/channels/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + localStorage.getItem("token"),
      },
      body: JSON.stringify({
        name: this.name,
        members: [this.txtusername],
      }),
    }).then((res) => {
      if (res.ok) {
        this.router.navigate(["/"]);
      } else {
        this.name = "";
        this.txtusername = "";
        alert("C'est pas bon");
      }
    });
  }
}
