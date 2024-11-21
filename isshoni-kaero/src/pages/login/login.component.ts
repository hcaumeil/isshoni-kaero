import { Component, inject } from "@angular/core";
import { Router } from "@angular/router";
import { environment } from "../../environments/environment";
import { FormsModule } from "@angular/forms";

@Component({
  selector: "app-login",
  standalone: true,
  imports: [FormsModule],
  templateUrl: "./login.component.html",
  styleUrl: "./login.component.css",
})
export class LoginComponent {
  router = inject(Router);
  txtusername: any;
  txtpassword: any;

  login() {
    fetch(environment.api_url + "/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: this.txtusername,
        password: this.txtpassword,
      }),
    }).then((res) => this.handle_res(res, this));
  }

  register() {
    this.router.navigate(["/register"]);
  }

  handle_res(res: Response, comp: any) {
    console.log("response processing");
    if (res.ok) {
      res.json().then((val) => {
        localStorage.setItem("token", val.token);
        localStorage.setItem("user", comp.txtusername);
        comp.router.navigate(["/"]);
      });
    } else {
      console.log("login error");
      comp.txtusername = "";
      comp.txtpassword = "";
      alert("C'est pas bon");
    }
  }
}
