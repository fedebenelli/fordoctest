module fpm_project
  implicit none
  private

  public :: say_hello
contains
  subroutine say_hello
    print *, "Hello, fpm_project!"
  end subroutine say_hello
end module fpm_project
