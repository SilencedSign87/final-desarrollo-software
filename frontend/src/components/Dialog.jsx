import { useControllableState } from "@radix-ui/react-use-controllable-state";
import { createContext, useContext, useMemo } from "react";
import { createPortal } from "react-dom";
import { twMerge } from "tailwind-merge";
import { cva } from "class-variance-authority";

const backdropVariants = cva(
    'fixed inset-0 transition-opacity duration-300 ease-out m-0 z-99',
    {
        variants: {
            scrollLock: {
                true: 'bg-black/40',
                false: 'bg-transparent pointer-events-none',
            },
            state: {
                open: 'opacity-100',
                closed: 'opacity-0 pointer-events-none',
            },
        },
        defaultVariants: {
            scrollLock: true,
            state: 'closed',
        },
    }
);

const dialogPanelVariants = cva(
    [
        'fixed z-100 bg-white  rounded-lg starting:scale-110 starting:opacity-0',
        'grid grid-rows-[1fr_auto] grid-cols-1',
        'border border-neutral-400 ',
        'transition-all',
        'max-h-[90vh] w-fit max-w-[95vw]',
        'focus:outline-none',
    ],
    {
        variants: {
            position: {
                top: 'top-5 left-0 right-0 mx-auto items-start',
                center: 'top-1/2 left-0 right-0 mx-auto -translate-y-1/2 items-center',
                bottom: 'bottom-5 left-0 right-0 mx-auto items-end',
                left: 'top-1/2 left-5 -translate-y-1/2 items-start',
                right: 'top-1/2 right-5 -translate-y-1/2 items-end',
                'top-left': 'top-12 left-5 items-start right-5 sm:right-auto',
                'top-right': 'top-12 right-5 items-end left-5 sm:left-auto',
                'bottom-left': 'bottom-5 left-5 items-start right-5 sm:right-auto',
                'bottom-right': 'bottom-5 right-5 items-end left-5 sm:left-auto',
            },
            state: {
                open: 'opacity-100 scale-100 duration-200 ease-[cubic-bezier(0.86,0,0.14,1)]',
                closed: 'opacity-0 scale-110 pointer-events-none duration-100 ease-in',
            },
        },
        defaultVariants: {
            position: 'center',
            state: 'closed',
        },
    }
);

const DialogContext = createContext(undefined);

const Dialog = ({ children, open, onOpenChange, position, type }) => {
    const [internalOpen, setInternalOpen] = useControllableState({
        prop: open,
        defaultProp: false,
        onChange: onOpenChange
    });

    const value = useMemo(() => ({
        open: internalOpen,
        setOpen: setInternalOpen,
        type: type || 'modal',
        position: position || 'center',
    }), [internalOpen, setInternalOpen, type, position]);

    return (
        <DialogContext.Provider value={value}>
            {children}
        </DialogContext.Provider>
    )
}

Dialog.Trigger = ({ children, className, ...props }) => {
    const ctx = useContext(DialogContext);
    if (!ctx) throw new Error("Dialog.Trigger must be used within a Dialog");

    const handleClick = () => {
        ctx.setOpen(!ctx.open);
    }
    return (
        <button
            className={
                className
            }
            onClick={handleClick}
            {...props}
        >
            {children}
        </button>
    )
}

Dialog.Surface = ({ children, className, backdropClassName }) => {
    const ctx = useContext(DialogContext);
    if (!ctx) throw new Error("Dialog.Surface must be used within a Dialog");

    const handleOutsideClick = () => {
        if (ctx.type === 'modal') {
            ctx.setOpen(false);
        }
    }

    if (!ctx.open) return null;

    return createPortal(
        <>
            {/* backdrop */}
            <div
                className={twMerge(
                    backdropVariants({ scrollLock: ctx.type === 'modal', state: ctx.open ? 'open' : 'closed' }),
                    backdropClassName
                )}
                onClick={handleOutsideClick}
            >
            </div>
            {/* dialog */}
            <div
                className={twMerge(
                    dialogPanelVariants({ position: ctx.position, state: ctx.open ? 'open' : 'closed' }),
                    className
                )}
                onClick={(e) => e.stopPropagation()}
            >
                {children}
            </div>
        </>,
        document.body
    )
}

Dialog.Header = ({ children, className }) => {
    return (
        <header className={twMerge("p-6 pb-4 text-xl font-semibold", className)}>
            {children}
        </header>
    )
}

Dialog.Content = ({ children, className }) => {
    return (
        <div className={twMerge("overflow-y-auto px-6 pb-4 text-sm", className)}>
            {children}
        </div>
    )
}

Dialog.Footer = ({ children, className, showCloseButton, closeButtonChildren, buttonClassName }) => {
    const ctx = useContext(DialogContext);
    if (!ctx) throw new Error("Dialog.Footer must be used within a Dialog");
    return (
        <footer className={twMerge("flex flex-wrap items-center justify-end gap-2 p-4 pt-0 bg-white/85 key-shadow border-l-0 border-r-0 border-b-0 rounded-b-lg", className)}>
            {children}
            {showCloseButton && (
                <button
                    className={twMerge(buttonClassName)}
                    onClick={() => ctx.setOpen(false)}
                >
                    {closeButtonChildren || 'Cerrar'}

                </button>
            )}
        </footer>
    )
}

export default Dialog;