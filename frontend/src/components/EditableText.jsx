import { useEffect, useRef, useState } from "react"
import { twMerge } from "tailwind-merge"

export default function EditableText({ value, onChange, className, ...props }) {
    const [isEditing, setIsEditing] = useState(false)
    const [text, setText] = useState(value)
    const spanRef = useRef(null)

    const handleKeyDown = (event) => {
        if (event.key === 'F2') {
            setIsEditing(!isEditing)
        } else if (event.key === 'Enter' && isEditing) {
            setIsEditing(false)
            onChange(text)
        } else if (event.key === 'Escape' && isEditing) {
            setIsEditing(false)
            setText(value)
            if (spanRef.current) {
                spanRef.current.innerText = value
            }
        }
    }

    const handleDoubleClick = () => {
        setIsEditing(true)
    }

    const handleBlur = () => {
        if (isEditing) {
            setIsEditing(false)
            onChange(text)
        }
    }

    const handleInput = () => {
        if (spanRef.current) {
            setText(spanRef.current.innerText)
        }
    }

    useEffect(() => {
        if (isEditing && spanRef.current) {
            spanRef.current.focus()
            const range = document.createRange()
            range.selectNodeContents(spanRef.current)
            const sel = window.getSelection()
            sel?.removeAllRanges()
            sel?.addRange(range)
        }
    }, [isEditing])

    useEffect(() => {
        if (!isEditing && spanRef.current) {
            spanRef.current.innerText = value
        }
    }, [value, isEditing])

    return (
        <div
            className={className}
            onKeyDown={handleKeyDown}
            tabIndex={0}
            {...props}
        >
            <span
                ref={spanRef}
                contentEditable={isEditing}
                suppressContentEditableWarning
                onDoubleClick={handleDoubleClick}
                onBlur={handleBlur}
                onInput={handleInput}
                className={twMerge(
                    "px-1",
                    isEditing ? "outline-none ring-1 ring-black rounded-none" : ""
                )}
                style={{ display: 'inline-block', minWidth: '2rem' }}
            >
                {value}
            </span>
        </div>
    )
}