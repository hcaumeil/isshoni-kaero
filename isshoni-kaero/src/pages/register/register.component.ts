import { Component, inject } from "@angular/core";
import { environment } from "../../environments/environment";
import { Router } from "@angular/router";
import { FormsModule } from "@angular/forms";

@Component({
  selector: "app-register",
  standalone: true,
  imports: [FormsModule],
  templateUrl: "./register.component.html",
  styleUrl: "./register.component.css",
})
export class RegisterComponent {
  router = inject(Router);
  txtusername: any;
  txtpassword: any;
  txtname: any;

  register() {
    fetch(environment.api_url + "/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: this.txtname,
        email: this.txtusername,
        password: this.txtpassword,
      }),
    }).then((res) => this.handle_res(res, this));
  }

  handle_res(res: Response, comp: any) {
    console.log("response processing");
    if (res.ok) {
      comp.router.navigate(["/login"]);
    } else {
      comp.txtusername = "";
      comp.txtname = "";
      comp.txtpassword = "";
      res.json().then((val) => alert("C'est pas bon : " + val.error));
    }
  }
}
