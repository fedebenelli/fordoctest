module full_doc
    !! Doc

    type :: atype
        !! Documented type
        real :: x !! Documented attribute
    contains
        procedure :: f !! Documented procedure
    end type

contains

    subroutine f(self, y)
        !! subroutine docstring
        class(atype) :: self !! doc
        real :: y !! doc
    end subroutine
    
    function fun(x)
        !! function docstring
        real :: x !! doc
    end function

end module

program main
    !! Documented program
    use full_doc

contains
    subroutine sub(x, y)
        !! Documented sub
        real :: x !! Documented arg
        real :: y !! Documented arg
    end subroutine
    
    function foo(x, y)
        !! Docstring
        real :: x !! Documented arg
        real :: y !! Documented arg
        real :: foo
    end function
end program