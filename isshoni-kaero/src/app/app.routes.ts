import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { LoginComponent } from "../pages/login/login.component";
import { HomeComponent } from "../pages/home/home.component";
import { authGuard } from "../guards/auth.guard";
import { RegisterComponent } from "../pages/register/register.component";
import { AddComponent } from "../pages/add/add.component";
// import { NotfoundComponent } from "../pages/notfound/notfound.component";
// import { LoginComponent } from "../pages/login/login.component";
// import { authGuard } from "../guards/auth.guard";
// import { FeedComponent } from "../pages/feed/feed.component";

export const routes: Routes = [
  { path: "", component: HomeComponent, canActivate: [authGuard] },
  { path: "login", component: LoginComponent },
  { path: "add", component: AddComponent },
  { path: "register", component: RegisterComponent },
  // { path: "login", component: FeedComponent, canActivate: [authGuard] },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
